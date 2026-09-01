"""
Fast vectorised application/interview/offer/placement generator.
Reads already-generated entity CSVs and produces the transaction layer.
Uses numpy broadcasting — no Python loops over students.
Target: complete in < 3 minutes for 50k students / 2500 postings.
"""
import os, sys, hashlib
import numpy as np
import pandas as pd
from datetime import date, timedelta

OUT  = sys.argv[1] if len(sys.argv) > 1 else 'data/synthetic'
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 42
rng  = np.random.default_rng(SEED)

def uid(prefix, key):
    h = hashlib.md5(str(key).encode()).hexdigest()[:10]
    return f"{prefix}_{h}"

def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -10, 10)))

print("Loading entity tables...")
students   = pd.read_csv(f"{OUT}/students.csv")
jobs       = pd.read_csv(f"{OUT}/job_postings.csv")
companies  = pd.read_csv(f"{OUT}/companies.csv")
jpd        = pd.read_csv(f"{OUT}/job_posting_departments.csv")
skills_df  = pd.read_csv(f"{OUT}/student_skills.csv")
internships= pd.read_csv(f"{OUT}/internships.csv")

print(f"  Students: {len(students):,}  Jobs: {len(jobs):,}")

# Pre-compute per-student aggregates (vectorised)
tech_skill_avg = (skills_df[skills_df['proficiency_score'] > 0]
                  .groupby('student_id')['proficiency_score'].mean()
                  .rename('tech_skill_avg'))
intern_count   = internships.groupby('student_id').size().rename('intern_count')

students = students.join(tech_skill_avg, on='student_id').join(intern_count, on='student_id')
students['tech_skill_avg'] = students['tech_skill_avg'].fillna(50.0)
students['intern_count']   = students['intern_count'].fillna(0).astype(int)

# Only eligible students
eligible = students[students['placement_status'].isin(['ELIGIBLE','ACTIVE','PLACED'])].copy()
eligible = eligible.reset_index(drop=True)
print(f"  Eligible students: {len(eligible):,}")

# Z-scores
cgpa_mean, cgpa_std = 7.477, 0.871
eligible['cgpa_z']   = (eligible['cgpa'] - cgpa_mean) / cgpa_std
eligible['sk_z']     = (eligible['tech_skill_avg'] - 55.0) / 20.0
eligible['int_bonus']= np.clip(eligible['intern_count'] * 0.12, 0, 0.40)

# Department → posting index
dept_to_postings = jpd.groupby('department_id')['job_posting_id'].apply(list).to_dict()
co_type_map  = companies.set_index('company_id')['company_type'].to_dict()
co_median_map= companies.set_index('company_id')['median_ctc_lpa'].to_dict()

# ── Vectorised application generation ───────────────────────────────────────
# Strategy: for each posting, sample a fraction of eligible students using
# numpy — no per-student Python loop.

SELECTIVITY = {"PRODUCT":0.55,"SERVICES":0.85,"STARTUP":0.70,
               "CONSULTING":0.72,"BANKING":0.65,"FINTECH":0.60,
               "CORE":0.72,"GOVERNMENT":0.78}
INT_ROUNDS_BY_TYPE = {
    "PRODUCT":    ["ONLINE_ASSESSMENT","TECHNICAL_1","TECHNICAL_2","MANAGERIAL","HR"],
    "SERVICES":   ["ONLINE_ASSESSMENT","TECHNICAL_1","HR"],
    "STARTUP":    ["TECHNICAL_1","TECHNICAL_2","HR"],
    "CONSULTING": ["ONLINE_ASSESSMENT","TECHNICAL_1","MANAGERIAL","HR"],
    "BANKING":    ["ONLINE_ASSESSMENT","TECHNICAL_1","MANAGERIAL","HR"],
}

app_rows, hist_rows = [], []
offer_rows, place_rows, iv_rows = [], [], []
SOURCES = ["CAMPUS_PORTAL","DIRECT","REFERRAL","EMAIL"]
SOURCE_P = [0.65, 0.18, 0.12, 0.05]

for jidx, jp in jobs.iterrows():
    if jidx % 250 == 0:
        print(f"  Job {jidx}/{len(jobs)}  apps={len(app_rows):,}  offers={len(offer_rows):,}")

    jp_id    = jp['job_posting_id']
    co_id    = jp['company_id']
    min_cgpa = float(jp.get('min_cgpa', 6.0))
    max_bl   = int(jp.get('max_backlogs', 2))
    pkg_med  = float(jp.get('package_median_lpa', 8.0))
    openings = int(jp.get('openings', 5))
    co_type  = co_type_map.get(co_id, 'SERVICES')
    sel_factor = SELECTIVITY.get(co_type, 0.75)
    rounds   = INT_ROUNDS_BY_TYPE.get(co_type, ["TECHNICAL_1","HR"])

    try:
        p_date = date.fromisoformat(str(jp.get('posting_date','2024-08-01'))[:10])
    except:
        p_date = date(2024, 8, 1)

    # Eligible dept filter
    eligible_dept_ids = set(jpd[jpd['job_posting_id'] == jp_id]['department_id'].tolist())
    pool = eligible[
        (eligible['cgpa'] >= min_cgpa) &
        (eligible['backlogs'] <= max_bl) &
        (eligible['department_id'].isin(eligible_dept_ids))
    ]
    if len(pool) == 0:
        continue

    # Sample applicants — vectorised random
    attract = min(0.20, openings / 200.0)
    apply_rate = 0.20 + attract
    n_apply = max(1, int(len(pool) * apply_rate * rng.uniform(0.7, 1.3)))
    n_apply = min(n_apply, len(pool))

    applicants = pool.sample(n=n_apply, random_state=int(rng.integers(0, 99999)))
    n = len(applicants)

    # ── Vectorised probability computation ──────────────────────────────
    cgpa_z   = applicants['cgpa_z'].values
    sk_z     = applicants['sk_z'].values
    int_bon  = applicants['int_bonus'].values

    # Shortlist prob
    p_short  = np.clip(sigmoid(cgpa_z*1.2 + sk_z*0.9 + int_bon), 0.04, 0.88)

    rand_apply   = rng.random(n)
    rand_short   = rng.random(n)
    rand_iv      = rng.random(n)
    rand_offer   = rng.random(n)
    rand_accept  = rng.random(n)
    rand_withdraw= rng.random(n)

    # Interview score proxy
    mock_iv_score = np.clip(
        applicants['tech_skill_avg'].values * 0.65 + applicants['cgpa'].values * 5
        + rng.normal(0, 10, n),
        0, 100
    )
    p_offer = np.clip(sigmoid((mock_iv_score/100 - 0.55)*5) * sel_factor, 0.02, 0.80)

    # Status vector
    statuses     = np.full(n, 'APPLIED', dtype=object)
    withdrawn    = rand_withdraw < 0.05
    shortlisted  = (~withdrawn) & (rand_short < p_short)
    interviewed  = shortlisted & (rand_iv < 0.72)
    offered      = interviewed & (rand_offer < p_offer)
    accepted     = offered & (rand_accept < 0.82)
    declined     = offered & ~accepted

    statuses[withdrawn]  = 'WITHDRAWN'
    statuses[shortlisted & ~interviewed] = 'REJECTED'
    statuses[interviewed & ~offered]     = 'REJECTED'
    statuses[interviewed & offered & ~accepted & ~declined] = 'OFFERED'
    statuses[declined]   = 'DECLINED'
    statuses[accepted]   = 'ACCEPTED'
    # Those shortlisted but not interviewed
    statuses[(shortlisted) & (statuses == 'APPLIED')] = 'SHORTLISTED'

    sids = applicants['student_id'].values
    dept_ids = applicants['department_id'].values

    for k in range(n):
        sid    = sids[k]
        status = statuses[k]
        app_id = uid("app", f"{sid}_{jp_id}")

        app_date = p_date + timedelta(days=int(rng.integers(0, 20)))

        app_rows.append({
            "application_id":     app_id,
            "student_id":         sid,
            "job_posting_id":     jp_id,
            "application_date":   str(app_date),
            "application_status": status,
            "withdrawn_date":     str(app_date + timedelta(days=int(rng.integers(1,10)))) if status == 'WITHDRAWN' else None,
            "rejection_reason":   "Not shortlisted" if status == 'REJECTED' else None,
            "source":             rng.choice(SOURCES, p=SOURCE_P),
            "created_at":         str(app_date),
            "updated_at":         str(app_date),
        })
        hist_rows.append({"application_id": app_id, "status": "APPLIED",
                          "status_timestamp": str(app_date)})

        if status in ('SHORTLISTED','INTERVIEW','OFFERED','ACCEPTED','DECLINED','REJECTED') and status != 'APPLIED':
            sl_date = app_date + timedelta(days=int(rng.integers(7, 20)))
            hist_rows.append({"application_id": app_id, "status": "SHORTLISTED",
                               "status_timestamp": str(sl_date)})

        if status in ('INTERVIEW','OFFERED','ACCEPTED','DECLINED','REJECTED') and interviewed[k]:
            iv_date = app_date + timedelta(days=int(rng.integers(14, 30)))
            hist_rows.append({"application_id": app_id, "status": "INTERVIEW",
                               "status_timestamp": str(iv_date)})
            # Generate interview rounds
            n_rounds = min(len(rounds), int(rng.integers(1, len(rounds)+1)))
            for r_num, rtype in enumerate(rounds[:n_rounds], 1):
                t_score = float(np.clip(rng.normal(mock_iv_score[k]*0.95, 10), 0, 100))
                c_score = float(np.clip(rng.normal(52 + cgpa_z[k]*4, 12), 0, 100))
                p_score = float(np.clip(rng.normal(50 + cgpa_z[k]*6, 13), 0, 100))
                overall = round(t_score*0.50 + c_score*0.25 + p_score*0.25, 1)
                result  = "PASS" if (status in ('OFFERED','ACCEPTED','DECLINED') or
                                     (r_num < n_rounds)) else "FAIL"
                sched   = iv_date + timedelta(days=r_num*2)
                iv_rows.append({
                    "interview_id":          uid("iv", f"{app_id}_{r_num}"),
                    "application_id":        app_id,
                    "round_number":          r_num,
                    "round_type":            rtype,
                    "scheduled_at":          str(sched),
                    "completed_at":          str(sched + timedelta(hours=2)),
                    "result":                result,
                    "technical_score":       round(t_score, 1),
                    "communication_score":   round(c_score, 1),
                    "problem_solving_score": round(p_score, 1),
                    "overall_score":         overall,
                    "feedback":              f"Round {r_num} completed",
                    "interviewer_type":      "INTERNAL",
                    "created_at":            str(sched),
                })

        if status in ('OFFERED','ACCEPTED','DECLINED') and offered[k]:
            off_date = app_date + timedelta(days=int(rng.integers(20, 40)))
            hist_rows.append({"application_id": app_id, "status": "OFFERED",
                               "status_timestamp": str(off_date)})
            ctc      = round(float(np.clip(rng.normal(pkg_med, pkg_med*0.12), pkg_med*0.7, pkg_med*1.6)), 2)
            base_lpa = round(ctc * rng.uniform(0.65, 0.78), 2)
            var_lpa  = round(ctc * rng.uniform(0.10, 0.20), 2)
            bon_lpa  = round(max(0, ctc - base_lpa - var_lpa), 2)
            off_id   = uid("off", app_id)
            off_status = "ACCEPTED" if accepted[k] else "DECLINED"
            join_dt  = str(p_date + timedelta(days=120))
            offer_rows.append({
                "offer_id":       off_id,
                "application_id": app_id,
                "student_id":     sid,
                "company_id":     co_id,
                "job_posting_id": jp_id,
                "offer_date":     str(off_date),
                "joining_date":   join_dt,
                "ctc_lpa":        ctc,
                "base_lpa":       base_lpa,
                "variable_lpa":   var_lpa,
                "bonus_lpa":      bon_lpa,
                "offer_status":   off_status,
                "accepted_date":  str(off_date + timedelta(days=3)) if off_status=="ACCEPTED" else None,
                "created_at":     str(off_date),
                "updated_at":     str(off_date),
            })
            if off_status == "ACCEPTED":
                hist_rows.append({"application_id": app_id, "status": "ACCEPTED",
                                   "status_timestamp": str(off_date + timedelta(days=3))})
                place_rows.append({
                    "placement_id":     uid("plc", app_id),
                    "student_id":       sid,
                    "company_id":       co_id,
                    "job_posting_id":   jp_id,
                    "offer_id":         off_id,
                    "placement_date":   str(off_date + timedelta(days=3)),
                    "joining_date":     join_dt,
                    "role_name":        jp['job_title'],
                    "ctc_lpa":          ctc,
                    "placement_type":   rng.choice(["FULL_TIME","INTERNSHIP_TO_FULL_TIME","PRE_PLACEMENT_OFFER"],
                                                    p=[0.70,0.20,0.10]),
                    "placement_status": "CONFIRMED",
                    "created_at":       str(off_date + timedelta(days=3)),
                    "updated_at":       str(off_date + timedelta(days=3)),
                })

print(f"\nWriting CSVs...")
pd.DataFrame(app_rows).drop_duplicates('application_id').to_csv(f"{OUT}/applications.csv", index=False)
pd.DataFrame(hist_rows).to_csv(f"{OUT}/application_status_history.csv", index=False)
pd.DataFrame(iv_rows).drop_duplicates('interview_id').to_csv(f"{OUT}/interviews.csv", index=False)
pd.DataFrame(offer_rows).drop_duplicates('offer_id').to_csv(f"{OUT}/offers.csv", index=False)
pd.DataFrame(place_rows).drop_duplicates('placement_id').to_csv(f"{OUT}/placements.csv", index=False)

n_apps   = len(app_rows)
n_short  = sum(1 for r in app_rows if r['application_status'] in ('SHORTLISTED','INTERVIEW','OFFERED','ACCEPTED'))
n_iv     = len(iv_rows)
n_off    = len(offer_rows)
n_plc    = len(place_rows)
print(f"\n{'='*55}")
print(f" Applications:  {n_apps:>10,}")
print(f" Shortlisted:   {n_short:>10,}  ({n_short/n_apps*100:.1f}%)")
print(f" IV rounds:     {n_iv:>10,}")
print(f" Offers:        {n_off:>10,}  ({n_off/n_apps*100:.1f}%)")
print(f" Placements:    {n_plc:>10,}  ({n_plc/n_apps*100:.1f}%)")
print(f"{'='*55}")
print("Done.")
