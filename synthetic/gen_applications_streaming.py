import os, sys, csv
import numpy as np
import pandas as pd
from datetime import date, timedelta

OUT  = sys.argv[1] if len(sys.argv) > 1 else 'data/synthetic'
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 42
rng  = np.random.default_rng(SEED)

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -10.0, 10.0)))

print("Loading entities...")
students    = pd.read_csv(f"{OUT}/students.csv")
jobs        = pd.read_csv(f"{OUT}/job_postings.csv")
companies   = pd.read_csv(f"{OUT}/companies.csv")
jpd         = pd.read_csv(f"{OUT}/job_posting_departments.csv")
skills_df   = pd.read_csv(f"{OUT}/student_skills.csv")
internships = pd.read_csv(f"{OUT}/internships.csv")

print(f"Loaded {len(students):,} students, {len(jobs):,} job postings.")

# Precompute student attributes
tech_skill_avg = (skills_df[skills_df['proficiency_score'] > 0]
                  .groupby('student_id')['proficiency_score'].mean()
                  .rename('tech_skill_avg'))
intern_count   = internships.groupby('student_id').size().rename('intern_count')

students = students.join(tech_skill_avg, on='student_id').join(intern_count, on='student_id')
students['tech_skill_avg'] = students['tech_skill_avg'].fillna(50.0)
students['intern_count']   = students['intern_count'].fillna(0).astype(int)

# Filter eligible students
eligible_mask = students['placement_status'].isin(['ELIGIBLE', 'ACTIVE', 'PLACED'])
eligible = students[eligible_mask].copy().reset_index(drop=True)
print(f"Eligible applicants pool: {len(eligible):,}")

cgpa_mean, cgpa_std = 7.477, 0.871
eligible['cgpa_z']    = (eligible['cgpa'] - cgpa_mean) / cgpa_std
eligible['sk_z']      = (eligible['tech_skill_avg'] - 55.0) / 20.0
eligible['int_bonus'] = np.clip(eligible['intern_count'] * 0.12, 0.0, 0.40)

# Build quick lookups
co_type_map   = companies.set_index('company_id')['company_type'].to_dict()
co_median_map = companies.set_index('company_id')['median_ctc_lpa'].to_dict()
jp_dept_map   = jpd.groupby('job_posting_id')['department_id'].apply(set).to_dict()

SELECTIVITY = {
    "PRODUCT": 0.55, "SERVICES": 0.85, "STARTUP": 0.70,
    "CONSULTING": 0.72, "BANKING": 0.65, "FINTECH": 0.60,
    "CORE": 0.72, "GOVERNMENT": 0.78
}

dept_to_indices = {}
for dept_id, grp in eligible.groupby('department_id'):
    dept_to_indices[dept_id] = grp.index.to_numpy()

# Open CSV writers directly for streaming write
f_app   = open(f"{OUT}/applications.csv", "w", newline="", encoding="utf-8")
f_hist  = open(f"{OUT}/application_status_history.csv", "w", newline="", encoding="utf-8")
f_iv    = open(f"{OUT}/interviews.csv", "w", newline="", encoding="utf-8")
f_offer = open(f"{OUT}/offers.csv", "w", newline="", encoding="utf-8")
f_place = open(f"{OUT}/placements.csv", "w", newline="", encoding="utf-8")

w_app   = csv.writer(f_app)
w_hist  = csv.writer(f_hist)
w_iv    = csv.writer(f_iv)
w_offer = csv.writer(f_offer)
w_place = csv.writer(f_place)

# Write headers matching Silver schemas exactly
w_app.writerow(["application_id","student_id","job_posting_id","application_date","application_status","withdrawn_date","rejection_reason","source","created_at","updated_at"])
w_hist.writerow(["application_id","status","status_timestamp"])
w_iv.writerow(["interview_id","application_id","round_number","round_type","scheduled_at","completed_at","result","technical_score","communication_score","problem_solving_score","overall_score","feedback","interviewer_type","created_at"])
w_offer.writerow(["offer_id","application_id","student_id","company_id","job_posting_id","offer_date","joining_date","ctc_lpa","base_lpa","variable_lpa","bonus_lpa","offer_status","accepted_date","created_at","updated_at"])
w_place.writerow(["placement_id","student_id","company_id","job_posting_id","offer_id","placement_date","joining_date","role_name","ctc_lpa","placement_type","placement_status","created_at","updated_at"])

app_counter = 0
total_apps = 0
total_ivs = 0
total_offers = 0
total_places = 0

print("Streaming pipeline data generation...")
for jidx, jp in jobs.iterrows():
    if jidx % 500 == 0:
        print(f"  Processed {jidx:,} / {len(jobs):,} job postings... (Apps: {total_apps:,})")
        
    jp_id      = jp['job_posting_id']
    co_id      = jp['company_id']
    min_cgpa   = float(jp.get('min_cgpa', 6.0))
    max_bl     = int(jp.get('max_backlogs', 2))
    pkg_med    = float(jp.get('package_median_lpa', 8.0))
    openings   = int(jp.get('openings', 5))
    co_type    = co_type_map.get(co_id, 'SERVICES')
    sel_factor = SELECTIVITY.get(co_type, 0.75)
    
    try:
        p_date = date.fromisoformat(str(jp.get('posting_date', '2024-08-01'))[:10])
    except Exception:
        p_date = date(2024, 8, 1)

    eligible_depts = jp_dept_map.get(jp_id, set())
    if not eligible_depts:
        eligible_depts = set(dept_to_indices.keys())
        
    matching_idx_list = [dept_to_indices[d] for d in eligible_depts if d in dept_to_indices]
    if not matching_idx_list:
        continue
    candidate_indices = np.concatenate(matching_idx_list)
    
    cand_cgpa = eligible['cgpa'].values[candidate_indices]
    cand_bl   = eligible['backlogs'].values[candidate_indices]
    
    valid_mask = (cand_cgpa >= min_cgpa) & (cand_bl <= max_bl)
    pool_indices = candidate_indices[valid_mask]
    n_pool = len(pool_indices)
    if n_pool == 0:
        continue
        
    # Calibrated application rate: ~100 applicants per job posting on average
    target_applicants = min(120, max(15, openings * 8))
    n_apply = min(n_pool, target_applicants)
    
    sampled_pool_idx = rng.choice(pool_indices, size=n_apply, replace=False)
    
    sub_df = eligible.iloc[sampled_pool_idx]
    n = len(sub_df)
    
    sids      = sub_df['student_id'].to_numpy()
    cgpas     = sub_df['cgpa'].to_numpy()
    cgpa_zs   = sub_df['cgpa_z'].to_numpy()
    sk_zs     = sub_df['sk_z'].to_numpy()
    int_bons  = sub_df['int_bonus'].to_numpy()
    sk_avgs   = sub_df['tech_skill_avg'].to_numpy()
    
    p_short = np.clip(sigmoid(cgpa_zs * 1.2 + sk_zs * 0.9 + int_bons), 0.04, 0.88)
    mock_iv_score = np.clip(sk_avgs * 0.65 + cgpas * 5.0 + rng.normal(0, 8.0, n), 0.0, 100.0)
    p_offer = np.clip(sigmoid((mock_iv_score / 100.0 - 0.55) * 5.0) * sel_factor, 0.02, 0.80)
    
    r_withdrawn = rng.random(n)
    r_short     = rng.random(n)
    r_iv        = rng.random(n)
    r_offer     = rng.random(n)
    r_accept    = rng.random(n)
    
    is_withdrawn = r_withdrawn < 0.04
    is_short     = (~is_withdrawn) & (r_short < p_short)
    is_iv        = is_short & (r_iv < 0.75)
    is_offer     = is_iv & (r_offer < p_offer)
    is_accept    = is_offer & (r_accept < 0.82)
    is_decline   = is_offer & (~is_accept)
    
    app_days = rng.integers(0, 20, n)
    sources = rng.choice(["CAMPUS_PORTAL", "DIRECT", "REFERRAL", "EMAIL"], size=n, p=[0.65, 0.18, 0.12, 0.05])
    
    for k in range(n):
        sid = sids[k]
        aid = f"app_{app_counter:08x}"
        app_counter += 1
        total_apps += 1
        
        adate = p_date + timedelta(days=int(app_days[k]))
        adate_str = str(adate)
        
        if is_accept[k]:
            status = 'ACCEPTED'
            rej_reason = ''
        elif is_decline[k]:
            status = 'DECLINED'
            rej_reason = ''
        elif is_offer[k]:
            status = 'OFFERED'
            rej_reason = ''
        elif is_iv[k]:
            status = 'REJECTED'
            rej_reason = 'Interview not cleared'
        elif is_short[k]:
            status = 'REJECTED'
            rej_reason = 'Not selected post shortlist'
        elif is_withdrawn[k]:
            status = 'WITHDRAWN'
            rej_reason = ''
        else:
            status = 'REJECTED'
            rej_reason = 'Not shortlisted'
            
        w_date = str(adate + timedelta(days=5)) if is_withdrawn[k] else ''
        
        w_app.writerow([aid, sid, jp_id, adate_str, status, w_date, rej_reason, sources[k], adate_str, adate_str])
        w_hist.writerow([aid, "APPLIED", adate_str])
        
        if is_short[k]:
            sl_date = str(adate + timedelta(days=10))
            w_hist.writerow([aid, "SHORTLISTED", sl_date])
            
        if is_iv[k]:
            iv_date = adate + timedelta(days=16)
            iv_date_str = str(iv_date)
            w_hist.writerow([aid, "INTERVIEW", iv_date_str])
            
            rounds = ["TECHNICAL_1", "TECHNICAL_2", "HR"]
            n_rounds = int(rng.integers(1, 4))
            for r_idx in range(n_rounds):
                r_num = r_idx + 1
                rtype = rounds[r_idx]
                r_sched = str(iv_date + timedelta(days=r_idx * 2))
                r_comp = str(iv_date + timedelta(days=r_idx * 2, hours=2))
                
                t_sc = float(np.clip(mock_iv_score[k] + rng.normal(0, 5), 0, 100))
                c_sc = float(np.clip(55.0 + cgpa_zs[k] * 5.0 + rng.normal(0, 8), 0, 100))
                p_sc = float(np.clip(52.0 + cgpa_zs[k] * 6.0 + rng.normal(0, 8), 0, 100))
                ov_sc = round(t_sc * 0.5 + c_sc * 0.25 + p_sc * 0.25, 1)
                
                res = "PASS" if (is_offer[k] or (r_num < n_rounds)) else "FAIL"
                
                w_iv.writerow([
                    f"iv_{aid}_{r_num}", aid, r_num, rtype, r_sched, r_comp, res,
                    round(t_sc, 1), round(c_sc, 1), round(p_sc, 1), ov_sc,
                    f"Round {r_num} completed", "INTERNAL", r_sched
                ])
                total_ivs += 1
                
        if is_offer[k]:
            off_date = adate + timedelta(days=25)
            off_date_str = str(off_date)
            w_hist.writerow([aid, "OFFERED", off_date_str])
            
            ctc = round(float(np.clip(rng.normal(pkg_med, pkg_med * 0.12), pkg_med * 0.7, pkg_med * 1.6)), 2)
            base_lpa = round(ctc * float(rng.uniform(0.65, 0.78)), 2)
            var_lpa  = round(ctc * float(rng.uniform(0.10, 0.20)), 2)
            bon_lpa  = round(max(0.0, ctc - base_lpa - var_lpa), 2)
            off_id   = f"off_{aid}"
            off_status = "ACCEPTED" if is_accept[k] else "DECLINED"
            join_dt  = str(p_date + timedelta(days=120))
            acc_dt   = str(off_date + timedelta(days=3)) if is_accept[k] else ''
            
            w_offer.writerow([
                off_id, aid, sid, co_id, jp_id, off_date_str, join_dt,
                ctc, base_lpa, var_lpa, bon_lpa, off_status, acc_dt, off_date_str, off_date_str
            ])
            total_offers += 1
            
            if is_accept[k]:
                w_hist.writerow([aid, "ACCEPTED", acc_dt])
                plc_type = rng.choice(["FULL_TIME", "INTERNSHIP_TO_FULL_TIME", "PRE_PLACEMENT_OFFER"], p=[0.70, 0.20, 0.10])
                w_place.writerow([
                    f"plc_{aid}", sid, co_id, jp_id, off_id, acc_dt, join_dt,
                    str(jp.get('job_title', 'Software Engineer')), ctc,
                    plc_type, "CONFIRMED", acc_dt, acc_dt
                ])
                total_places += 1

f_app.close()
f_hist.close()
f_iv.close()
f_offer.close()
f_place.close()

print(f"\n=======================================================")
print(f" STREAMING TRANSACTION GENERATION COMPLETED SUCCESSFULLY")
print(f" Total Applications: {total_apps:,}")
print(f" Total Interviews:   {total_ivs:,}")
print(f" Total Offers:       {total_offers:,}")
print(f" Total Placements:   {total_places:,}")
print(f"=======================================================\n")
