"""
PLACEWISE — Massive Synthetic Data Generator
=============================================
Grounded in real distributions from:
  - indian_engineering_placement_2026.csv (15k students, Kaggle)
  - Placement Details - Placement Stats.csv (272 real company drives)

Generates ALL columns required by every Silver schema table.
Output: data/synthetic/<entity>.csv  (ready for Bronze ingestion)

Usage:
  python generate_full_dataset.py --scale medium  # ~50k students
  python generate_full_dataset.py --scale large   # ~200k students
  python generate_full_dataset.py --scale small   # ~10k students
"""

import sys, os, hashlib, argparse
from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
from scipy.stats import truncnorm
from faker import Faker

fake = Faker('en_IN')

# ── CLI ──────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument('--scale', choices=['small','medium','large'], default='medium')
parser.add_argument('--seed',  type=int, default=42)
parser.add_argument('--out',   default='data/synthetic')
args = parser.parse_args()

SCALE_PARAMS = {
    'small':  dict(n_students=10_000,  n_companies=200,  n_postings=600),
    'medium': dict(n_students=50_000,  n_companies=600,  n_postings=2_500),
    'large':  dict(n_students=200_000, n_companies=2_000, n_postings=10_000),
}
P = SCALE_PARAMS[args.scale]
N_STU = P['n_students']
N_CO  = P['n_companies']
N_POST = P['n_postings']
SEED  = args.seed
OUT   = args.out
os.makedirs(OUT, exist_ok=True)

rng = np.random.default_rng(SEED)
Faker.seed(SEED)

def uid(prefix, key):
    h = hashlib.md5(str(key).encode()).hexdigest()[:10]
    return f"{prefix}_{h}"

def trunc_normal(mean, std, lo, hi, n):
    a, b = (lo - mean)/std, (hi - mean)/std
    return truncnorm.rvs(a, b, loc=mean, scale=std, size=n, random_state=SEED)

def sigmoid(x):
    return 1/(1+np.exp(-np.clip(x,-10,10)))

print(f"\n{'='*60}")
print(f" PLACEWISE Synthetic Generator  |  scale={args.scale}  seed={SEED}")
print(f" Students: {N_STU:,}  Companies: {N_CO:,}  Postings: {N_POST:,}")
print(f"{'='*60}\n")

# ═══════════════════════════════════════════════════════════════════════
# 1. DEPARTMENTS  →  silver.departments
# ═══════════════════════════════════════════════════════════════════════
print("► departments ...")
DEPT_DATA = [
    ("CSE",  "Computer Science & Engineering",        "School of Engineering", 0.200),
    ("IT",   "Information Technology",                "School of Engineering", 0.123),
    ("AIML", "Artificial Intelligence & ML",          "School of Engineering", 0.101),
    ("ECE",  "Electronics & Communication Engineering","School of Engineering", 0.147),
    ("EEE",  "Electrical & Electronics Engineering",  "School of Engineering", 0.100),
    ("ME",   "Mechanical Engineering",                "School of Engineering", 0.153),
    ("CE",   "Civil Engineering",                     "School of Engineering", 0.096),
    ("CH",   "Chemical Engineering",                  "School of Engineering", 0.080),
]
depts = pd.DataFrame([{
    "department_id":   uid("dept", code),
    "department_code": code,
    "department_name": name,
    "school_name":     school,
    "is_active":       True,
    "dept_prop":       prop,
} for code,name,school,prop in DEPT_DATA])
depts.to_csv(f"{OUT}/departments.csv", index=False)
DEPT_IDS = depts['department_id'].tolist()
DEPT_CODES = depts['department_code'].tolist()
DEPT_PROPS = depts['dept_prop'].tolist()
print(f"  {len(depts)} departments")

# ═══════════════════════════════════════════════════════════════════════
# 2. ACADEMIC PROGRAMS  →  silver.academic_programs
# ═══════════════════════════════════════════════════════════════════════
print("► academic_programs ...")
prog_rows = []
for _, d in depts.iterrows():
    for deg, dur in [("BTECH",4),("MTECH",2)]:
        prog_rows.append({
            "program_id":    uid("prog", f"{d['department_code']}_{deg}"),
            "department_id": d['department_id'],
            "program_name":  f"{d['department_name']} ({deg})",
            "degree_type":   deg,
            "duration_years":dur,
            "is_active":     True,
        })
# MBA
prog_rows.append({"program_id": uid("prog","MBA"),"department_id": uid("dept","CSE"),
    "program_name":"Master of Business Administration","degree_type":"MBA","duration_years":2,"is_active":True})
progs = pd.DataFrame(prog_rows)
progs.to_csv(f"{OUT}/academic_programs.csv", index=False)
print(f"  {len(progs)} programs")

# ═══════════════════════════════════════════════════════════════════════
# 3. COHORTS  →  silver.cohorts
# ═══════════════════════════════════════════════════════════════════════
print("► cohorts ...")
cohort_rows = []
for deg, dur in [("BTECH",4),("MTECH",2),("MBA",2)]:
    for adm in range(2018, 2026):
        grad = adm + dur
        for _, d in depts.iterrows():
            pid = uid("prog", f"{d['department_code']}_{deg}")
            cohort_rows.append({
                "cohort_id":       uid("coh", f"{d['department_code']}_{deg}_{adm}"),
                "program_id":      pid,
                "department_id":   d['department_id'],
                "admission_year":  adm,
                "graduation_year": grad,
                "batch_label":     f"{d['department_code']}-{deg}-{adm}-{grad}",
                "degree_type":     deg,
            })
cohorts = pd.DataFrame(cohort_rows).drop_duplicates('cohort_id')
cohorts.to_csv(f"{OUT}/cohorts.csv", index=False)
print(f"  {len(cohorts)} cohorts")

# ═══════════════════════════════════════════════════════════════════════
# 4. SKILLS  →  silver.skills
# ═══════════════════════════════════════════════════════════════════════
print("► skills ...")
SKILLS_RAW = [
    # (name, category, subcategory, skill_type)
    ("Python","Programming","Scripting","LANGUAGE"),("Java","Programming","OOP","LANGUAGE"),
    ("C++","Programming","Systems","LANGUAGE"),("JavaScript","Programming","Web","LANGUAGE"),
    ("TypeScript","Programming","Web","LANGUAGE"),("R","Programming","Statistical","LANGUAGE"),
    ("Go","Programming","Systems","LANGUAGE"),("Scala","Programming","Functional","LANGUAGE"),
    ("SQL","Database","Query","TECHNICAL"),("PostgreSQL","Database","Relational","TOOL"),
    ("MySQL","Database","Relational","TOOL"),("MongoDB","Database","NoSQL","TOOL"),
    ("Redis","Database","Cache","TOOL"),("Cassandra","Database","NoSQL","TOOL"),
    ("Spark","Big Data","Processing","TOOL"),("Kafka","Big Data","Streaming","TOOL"),
    ("Airflow","Big Data","Orchestration","TOOL"),("Hadoop","Big Data","Storage","TOOL"),
    ("Hive","Big Data","Query","TOOL"),("AWS","Cloud","Platform","TOOL"),
    ("Azure","Cloud","Platform","TOOL"),("GCP","Cloud","Platform","TOOL"),
    ("Docker","DevOps","Containerization","TOOL"),("Kubernetes","DevOps","Orchestration","TOOL"),
    ("Git","DevOps","VCS","TOOL"),("CI/CD","DevOps","Pipeline","TOOL"),
    ("React","Frontend","Library","TOOL"),("Angular","Frontend","Framework","TOOL"),
    ("Vue","Frontend","Framework","TOOL"),("HTML/CSS","Frontend","Markup","TECHNICAL"),
    ("Redux","Frontend","State","TOOL"),("Node.js","Backend","Runtime","TOOL"),
    ("REST APIs","Backend","API","TECHNICAL"),("GraphQL","Backend","API","TECHNICAL"),
    ("TensorFlow","ML/AI","Deep Learning","TOOL"),("PyTorch","ML/AI","Deep Learning","TOOL"),
    ("Scikit-learn","ML/AI","Classical ML","TOOL"),("NLP","ML/AI","NLP","DOMAIN"),
    ("Computer Vision","ML/AI","CV","DOMAIN"),("Statistics","Analytics","Math","DOMAIN"),
    ("Power BI","BI Tools","Visualization","TOOL"),("Tableau","BI Tools","Visualization","TOOL"),
    ("Excel","BI Tools","Spreadsheet","TOOL"),("Looker","BI Tools","Visualization","TOOL"),
    ("Data Structures","CS Fundamentals","DSA","TECHNICAL"),
    ("Algorithms","CS Fundamentals","DSA","TECHNICAL"),
    ("OS Concepts","CS Fundamentals","Systems","TECHNICAL"),
    ("DBMS","CS Fundamentals","Database","TECHNICAL"),
    ("Computer Networks","CS Fundamentals","Networking","TECHNICAL"),
    ("Communication","Soft Skills","Verbal","SOFT"),
    ("Leadership","Soft Skills","Management","SOFT"),
    ("Problem Solving","Soft Skills","Analytical","SOFT"),
    ("Teamwork","Soft Skills","Interpersonal","SOFT"),
    ("Presentation","Soft Skills","Verbal","SOFT"),
    ("Time Management","Soft Skills","Self-Management","SOFT"),
    ("Critical Thinking","Soft Skills","Analytical","SOFT"),
    ("Adaptability","Soft Skills","Behavioral","SOFT"),
    ("Finance","Domain","Industry","DOMAIN"),
    ("Healthcare","Domain","Industry","DOMAIN"),
    ("Logistics","Domain","Industry","DOMAIN"),
    ("VLSI","Electronics","Chip Design","TECHNICAL"),
    ("Embedded Systems","Electronics","Hardware","TECHNICAL"),
    ("MATLAB","Engineering","Simulation","TOOL"),
    ("AutoCAD","Engineering","CAD","TOOL"),
    ("Competitive Programming","CS Fundamentals","Competitive","TECHNICAL"),
    ("System Design","CS Fundamentals","Architecture","TECHNICAL"),
]
skills = pd.DataFrame([{
    "skill_id": uid("sk", name),
    "skill_name": name, "skill_category": cat,
    "skill_subcategory": subcat, "skill_type": stype,
} for name,cat,subcat,stype in SKILLS_RAW])
skills.to_csv(f"{OUT}/skills.csv", index=False)
SKILL_IDS = skills['skill_id'].tolist()
print(f"  {len(skills)} skills")

# Role → skill affinity map (skill_name → list of role_families that want it)
ROLE_SKILLS = {
    "Software Engineering": ["Python","Java","C++","Data Structures","Algorithms","SQL","Git","REST APIs","System Design","Communication","Problem Solving"],
    "Data Engineering":     ["Python","SQL","Spark","Kafka","Airflow","AWS","Azure","Docker","Data Structures","Communication","Problem Solving"],
    "Data Analyst":         ["SQL","Python","Excel","Power BI","Tableau","Statistics","Communication","Presentation"],
    "Machine Learning":     ["Python","TensorFlow","PyTorch","Scikit-learn","SQL","Statistics","NLP","Computer Vision","Problem Solving","Communication"],
    "Frontend":             ["JavaScript","TypeScript","React","Angular","HTML/CSS","Redux","Git","Communication","Problem Solving"],
    "Backend":              ["Python","Java","Node.js","SQL","REST APIs","Docker","PostgreSQL","Git","System Design","Problem Solving"],
    "DevOps":               ["Docker","Kubernetes","CI/CD","AWS","Azure","Git","Python","Communication"],
    "Product Management":   ["Communication","Leadership","Problem Solving","Presentation","Statistics","Excel","Teamwork","Time Management"],
    "Business Analyst":     ["Communication","SQL","Excel","Power BI","Statistics","Presentation","Critical Thinking","Problem Solving"],
    "Embedded/VLSI":        ["VLSI","Embedded Systems","C++","MATLAB","Python","Communication"],
    "Mechanical":           ["AutoCAD","MATLAB","Problem Solving","Communication","Teamwork"],
    "Civil":                ["AutoCAD","MATLAB","Communication","Problem Solving","Teamwork"],
}
ROLE_FAMILIES = list(ROLE_SKILLS.keys())

# Branch → preferred role family mapping (grounded in real data)
BRANCH_ROLE_AFFINITY = {
    "CSE":        ["Software Engineering","Data Engineering","Machine Learning","Backend","Frontend","Data Analyst","DevOps","Product Management"],
    "IT":         ["Software Engineering","Backend","Frontend","Data Analyst","Data Engineering","DevOps"],
    "AIML":       ["Machine Learning","Data Engineering","Data Analyst","Backend","Software Engineering"],
    "ECE":        ["Software Engineering","Embedded/VLSI","Data Engineering","Machine Learning","DevOps"],
    "EEE":        ["Embedded/VLSI","Software Engineering","Data Analyst","DevOps","Mechanical"],
    "ME":         ["Mechanical","Business Analyst","Product Management","Data Analyst"],
    "CE":         ["Civil","Business Analyst","Product Management"],
    "CH":         ["Business Analyst","Data Analyst","Product Management"],
}

# ═══════════════════════════════════════════════════════════════════════
# 5. COMPANIES  →  silver.companies
# ═══════════════════════════════════════════════════════════════════════
print("► companies ...")

# Real companies from institutional data
REAL_COMPANIES = [
    ("Oracle","Technology","PRODUCT","ENTERPRISE",True,False,False,1977,14.5),
    ("Ring Central","Technology","PRODUCT","ENTERPRISE",True,False,False,1999,24.0),
    ("InMobi","Technology","STARTUP","MID",True,False,True,2007,22.0),
    ("Deutsche Bank","Banking","BANKING","ENTERPRISE",False,False,False,1870,15.5),
    ("Pure Storage","Technology","PRODUCT","ENTERPRISE",True,False,False,2009,16.0),
    ("Walmart Global Tech","Technology","PRODUCT","ENTERPRISE",True,False,False,1962,16.9),
    ("Lowe's","Technology","PRODUCT","ENTERPRISE",True,False,False,1921,11.5),
    ("Cohesity","Technology","PRODUCT","MID",True,False,False,2013,15.0),
    ("Licious","Technology","STARTUP","MID",False,False,True,2015,12.0),
    ("Qualcomm","Technology","PRODUCT","ENTERPRISE",True,False,False,1985,15.0),
    ("Cisco","Technology","PRODUCT","ENTERPRISE",True,False,False,1984,12.0),
    ("Microsoft","Technology","PRODUCT","ENTERPRISE",True,False,False,1975,30.0),
    ("Google","Technology","PRODUCT","ENTERPRISE",True,False,False,1998,45.0),
    ("Amazon","Technology","PRODUCT","ENTERPRISE",True,False,False,1994,32.0),
    ("Flipkart","E-Commerce","PRODUCT","ENTERPRISE",True,False,False,2007,25.0),
    ("Swiggy","Technology","STARTUP","MID",False,False,True,2014,20.0),
    ("Razorpay","Fintech","STARTUP","MID",True,False,True,2014,22.0),
    ("CRED","Fintech","STARTUP","MID",True,False,True,2018,24.0),
    ("Infosys","IT Services","SERVICES","ENTERPRISE",False,True,False,1981,4.5),
    ("TCS","IT Services","SERVICES","ENTERPRISE",False,True,False,1968,3.8),
    ("Wipro","IT Services","SERVICES","ENTERPRISE",False,True,False,1945,4.0),
    ("HCL Technologies","IT Services","SERVICES","ENTERPRISE",False,True,False,1976,4.2),
    ("Cognizant","IT Services","SERVICES","ENTERPRISE",False,True,False,1994,4.0),
    ("Accenture","Consulting","CONSULTING","ENTERPRISE",False,False,False,1989,5.5),
    ("Deloitte","Consulting","CONSULTING","ENTERPRISE",False,False,False,1845,7.0),
    ("McKinsey","Consulting","CONSULTING","ENTERPRISE",False,False,False,1926,12.0),
    ("Goldman Sachs","Banking","BANKING","ENTERPRISE",False,False,False,1869,25.0),
    ("JP Morgan","Banking","BANKING","ENTERPRISE",False,False,False,1799,20.0),
    ("HSBC","Banking","BANKING","ENTERPRISE",False,False,False,1865,8.0),
    ("PhonePe","Fintech","PRODUCT","MID",True,False,False,2015,18.0),
    ("Zepto","E-Commerce","STARTUP","MID",False,False,True,2021,15.0),
    ("Meesho","E-Commerce","STARTUP","MID",False,False,True,2015,16.0),
    ("Groww","Fintech","STARTUP","MID",True,False,True,2016,20.0),
    ("Zomato","Technology","PRODUCT","MID",False,False,False,2008,14.0),
    ("Paytm","Fintech","PRODUCT","MID",True,False,False,2010,10.0),
    ("L&T Technology Services","Engineering","SERVICES","ENTERPRISE",False,True,False,1938,5.5),
    ("Bosch","Manufacturing","CORE","ENTERPRISE",False,False,False,1886,6.5),
    ("Siemens","Manufacturing","CORE","ENTERPRISE",False,False,False,1847,7.0),
    ("Samsung","Technology","PRODUCT","ENTERPRISE",True,False,False,1969,12.0),
    ("Intel","Technology","PRODUCT","ENTERPRISE",True,False,False,1968,18.0),
    ("Texas Instruments","Technology","PRODUCT","ENTERPRISE",True,False,False,1951,15.0),
    ("VMware","Technology","PRODUCT","ENTERPRISE",True,False,False,1998,18.0),
    ("Nutanix","Technology","PRODUCT","ENTERPRISE",True,False,False,2009,20.0),
    ("Druva","Technology","PRODUCT","MID",True,False,False,2008,16.0),
    ("Sprinklr","Technology","PRODUCT","MID",True,False,False,2009,18.0),
    ("NVIDIA","Technology","PRODUCT","ENTERPRISE",True,False,False,1993,35.0),
    ("Adobe","Technology","PRODUCT","ENTERPRISE",True,False,False,1982,22.0),
    ("Salesforce","Technology","PRODUCT","ENTERPRISE",True,False,False,1999,20.0),
    ("SAP","Technology","PRODUCT","ENTERPRISE",True,False,False,1972,12.0),
    ("ThoughtWorks","Consulting","SERVICES","MID",False,True,False,1993,8.0),
]

INDUSTRIES = ["Technology","IT Services","Fintech","Banking","E-Commerce","Consulting","Manufacturing","Engineering","Healthcare","Logistics"]
COMP_TYPES  = ["PRODUCT","SERVICES","STARTUP","CONSULTING","BANKING","CORE","FINTECH","GOVERNMENT"]
COMP_SIZES  = ["STARTUP","MID","ENTERPRISE"]
CITIES      = ["Bengaluru","Mumbai","Hyderabad","Chennai","Pune","Delhi","Gurugram","Noida","Kolkata","Ahmedabad"]

company_rows = []
for i,(name,ind,ctype,size,isprod,isserv,isstartup,founded,median_ctc) in enumerate(REAL_COMPANIES):
    company_rows.append({
        "company_id":          uid("co", name),
        "company_name":        name,
        "industry":            ind,
        "company_type":        ctype,
        "company_size":        size,
        "headquarters_city":   rng.choice(CITIES),
        "headquarters_country":"India",
        "website":             f"https://www.{name.lower().replace(' ','').replace('&','and')}.com",
        "is_product_company":  isprod,
        "is_service_company":  isserv,
        "is_startup":          isstartup,
        "founded_year":        founded,
        "median_ctc_lpa":      median_ctc,
        "created_at":          "2024-01-01",
        "updated_at":          "2024-01-01",
    })

# Generate remaining synthetic companies
n_extra = N_CO - len(REAL_COMPANIES)
for i in range(n_extra):
    ctype  = rng.choice(COMP_TYPES, p=[0.25,0.30,0.15,0.10,0.08,0.05,0.05,0.02])
    size   = "STARTUP" if ctype in ["STARTUP"] else rng.choice(["MID","ENTERPRISE"], p=[0.4,0.6])
    isprod = ctype in ["PRODUCT","FINTECH","STARTUP"]
    isserv = ctype in ["SERVICES","CONSULTING"]
    median_ctc = float(rng.lognormal(2.2, 0.5)) if ctype=="PRODUCT" else float(rng.lognormal(1.5,0.4))
    median_ctc = round(float(np.clip(median_ctc, 3, 45)), 2)
    founded = int(rng.integers(1995, 2022))
    company_rows.append({
        "company_id":          uid("co", f"syn_{i}_{SEED}"),
        "company_name":        fake.company(),
        "industry":            rng.choice(INDUSTRIES),
        "company_type":        ctype,
        "company_size":        size,
        "headquarters_city":   rng.choice(CITIES),
        "headquarters_country":"India",
        "website":             f"https://www.synco{i}.com",
        "is_product_company":  bool(isprod),
        "is_service_company":  bool(isserv),
        "is_startup":          bool(size=="STARTUP"),
        "founded_year":        founded,
        "median_ctc_lpa":      median_ctc,
        "created_at":          "2024-01-01",
        "updated_at":          "2024-01-01",
    })
companies = pd.DataFrame(company_rows).drop_duplicates('company_id').head(N_CO)
companies.to_csv(f"{OUT}/companies.csv", index=False)
CO_IDS = companies['company_id'].tolist()
print(f"  {len(companies)} companies")

# ═══════════════════════════════════════════════════════════════════════
# 6. JOB ROLES  →  silver.job_roles
# ═══════════════════════════════════════════════════════════════════════
print("► job_roles ...")
JOB_ROLE_DATA = [
    ("Software Engineer","Software Engineering","ENTRY"),
    ("Senior Software Engineer","Software Engineering","MID"),
    ("Data Engineer","Data Engineering","ENTRY"),
    ("Senior Data Engineer","Data Engineering","MID"),
    ("Data Analyst","Data Analyst","ENTRY"),
    ("Senior Data Analyst","Data Analyst","MID"),
    ("Machine Learning Engineer","Machine Learning","ENTRY"),
    ("Senior ML Engineer","Machine Learning","MID"),
    ("Frontend Engineer","Frontend","ENTRY"),
    ("Backend Engineer","Backend","ENTRY"),
    ("Full Stack Engineer","Software Engineering","ENTRY"),
    ("DevOps Engineer","DevOps","ENTRY"),
    ("SRE","DevOps","MID"),
    ("Product Manager","Product Management","MID"),
    ("Business Analyst","Business Analyst","ENTRY"),
    ("Embedded Engineer","Embedded/VLSI","ENTRY"),
    ("VLSI Design Engineer","Embedded/VLSI","ENTRY"),
    ("Mechanical Engineer","Mechanical","ENTRY"),
    ("Civil Engineer","Civil","ENTRY"),
    ("Associate Software Engineer","Software Engineering","ENTRY"),
    ("SDE-1","Software Engineering","ENTRY"),
    ("SDE-2","Software Engineering","MID"),
    ("Data Scientist","Machine Learning","ENTRY"),
    ("Cloud Engineer","DevOps","ENTRY"),
    ("Research Engineer","Machine Learning","MID"),
    ("Graduate Engineer Trainee","Software Engineering","ENTRY"),
    ("Management Trainee","Business Analyst","ENTRY"),
    ("Technology Analyst","Software Engineering","ENTRY"),
]
job_roles = pd.DataFrame([{
    "job_role_id":    uid("role", rn),
    "role_name":      rn,
    "role_family":    rf,
    "seniority_level":sl,
    "created_at":     "2024-01-01",
} for rn,rf,sl in JOB_ROLE_DATA])
job_roles.to_csv(f"{OUT}/job_roles.csv", index=False)
print(f"  {len(job_roles)} job roles")

# ═══════════════════════════════════════════════════════════════════════
# 7. STUDENTS  →  silver.students
# (grounded in real CGPA/attendance/placement distributions from Kaggle)
# ═══════════════════════════════════════════════════════════════════════
print(f"► students ({N_STU:,}) ...")
# Real distributions from Kaggle profiling:
#   CGPA: mean=7.477, std=0.871, min=4.05, max=10.0
#   Attendance: mean=73.77, std=7.52, min=50.0, max=100.0
#   Gender: Male=65.2%, Female=32.8%, Other=2.0%
#   Branch proportions from real data (normalised)

GENDERS   = ["Male","Female","Other"]
GENDER_P  = [0.652, 0.328, 0.020]
STATES    = ["Karnataka","Maharashtra","Tamil Nadu","Uttar Pradesh","Andhra Pradesh",
             "Telangana","Kerala","Gujarat","Rajasthan","West Bengal","Bihar","Punjab",
             "Madhya Pradesh","Delhi","Odisha"]
PREF_LOCS = ["Bengaluru","Mumbai","Hyderabad","Chennai","Pune","Delhi","Gurugram","Any"]

cgpa_vals  = trunc_normal(7.477, 0.871, 4.0, 10.0, N_STU)
att_vals   = trunc_normal(73.77, 7.52, 50.0, 100.0, N_STU)
# percentage correlated with cgpa (r≈0.85)
pct_vals   = np.clip(cgpa_vals*9.5 + rng.normal(0, 4, N_STU), 40.0, 100.0)
# backlogs: inversely correlated with CGPA
backlog_p  = sigmoid(-2.5*(cgpa_vals - 6.5))  # prob of having backlog
backlogs   = np.where(rng.random(N_STU) < backlog_p,
                       rng.integers(1, 5, N_STU), 0)

dept_choices = rng.choice(len(depts), size=N_STU, p=DEPT_PROPS)
grad_years   = rng.choice([2023,2024,2025,2026], size=N_STU, p=[0.15,0.25,0.35,0.25])
admission_years = grad_years - 4

student_rows = []
for i in range(N_STU):
    if i % 10000 == 0: print(f"   {i:,}/{N_STU:,}")
    d_idx   = dept_choices[i]
    dept_id = DEPT_IDS[d_idx]
    dept_code = DEPT_CODES[d_idx]
    deg   = "BTECH" if rng.random() < 0.85 else ("MTECH" if rng.random() < 0.7 else "MBA")
    prog_id = uid("prog", f"{dept_code}_{deg}")
    grad_yr = int(grad_years[i])
    adm_yr  = grad_yr - (4 if deg=="BTECH" else 2)
    cohort_id = uid("coh", f"{dept_code}_{deg}_{adm_yr}")
    cgpa    = round(float(np.clip(cgpa_vals[i], 4.0, 10.0)), 2)
    pct     = round(float(np.clip(pct_vals[i], 40.0, 100.0)), 2)
    bl      = int(np.clip(backlogs[i], 0, 10))
    att     = round(float(np.clip(att_vals[i], 50.0, 100.0)), 2)
    gender  = rng.choice(GENDERS, p=GENDER_P)
    role_family = rng.choice(BRANCH_ROLE_AFFINITY.get(dept_code, ["Software Engineering"]))
    dob     = date(grad_yr - 22, int(rng.integers(1,13)), int(rng.integers(1,29)))

    # Placement status: grounded in real placement-by-CGPA rates
    if cgpa >= 9.0:   p_place = 0.925
    elif cgpa >= 8.0: p_place = 0.803
    elif cgpa >= 7.0: p_place = 0.664
    elif cgpa >= 6.0: p_place = 0.506
    else:             p_place = 0.316
    # Branch adjustment
    if dept_code in ["CSE","IT","AIML"]:   p_place = min(0.97, p_place * 1.15)
    elif dept_code in ["ME","CE","CH"]:    p_place = max(0.10, p_place * 0.75)
    # Backlog penalty
    if bl > 0: p_place = max(0.05, p_place * (1 - bl*0.10))

    if grad_yr > 2025:
        pstatus = "ELIGIBLE" if bl == 0 else "NOT_STARTED"
    else:
        if rng.random() < p_place:
            pstatus = "PLACED"
        elif rng.random() < 0.15:
            pstatus = "OPTED_OUT"
        elif cgpa >= 6.0 and bl <= 2:
            pstatus = rng.choice(["ACTIVE","ELIGIBLE"], p=[0.6,0.4])
        else:
            pstatus = "NOT_STARTED"

    student_rows.append({
        "student_id":            uid("stu", f"{i}_{SEED}"),
        "university_roll_no":    f"URN{grad_yr}{dept_code}{i:06d}",
        "full_name":             fake.name(),
        "gender":                gender,
        "date_of_birth":         str(dob),
        "cohort_id":             cohort_id,
        "department_id":         dept_id,
        "program_id":            prog_id,
        "current_semester":      min(8, max(1, (2026 - adm_yr)*2)),
        "cgpa":                  cgpa,
        "percentage":            pct,
        "backlogs":              bl,
        "attendance_percentage": att,
        "placement_status":      pstatus,
        "preferred_role":        role_family,
        "preferred_location":    rng.choice(PREF_LOCS),
        "work_authorization":    "Indian Citizen",
        "graduation_year":       grad_yr,
        "created_at":            "2024-01-01",
        "updated_at":            "2024-01-01",
    })

students = pd.DataFrame(student_rows)
students.to_csv(f"{OUT}/students.csv", index=False)
STU_IDS = students['student_id'].tolist()
print(f"  {len(students)} students saved")

# ═══════════════════════════════════════════════════════════════════════
# 8. STUDENT SKILLS  →  silver.student_skills
# ═══════════════════════════════════════════════════════════════════════
print("► student_skills ...")
skill_name_to_id = dict(zip(skills['skill_name'], skills['skill_id']))
VERIF_SOURCES = ["SELF","ASSESSMENT","CERTIFICATION","PROJECT","INTERNSHIP","COURSE","PLACEMENT_TEST"]
PROF_LEVELS   = ["BEGINNER","INTERMEDIATE","ADVANCED","EXPERT"]

stu_skill_rows = []
for i, row in students.iterrows():
    if i % 10000 == 0: print(f"   {i:,}/{N_STU:,}")
    sid      = row['student_id']
    cgpa     = row['cgpa']
    role_fam = row['preferred_role']

    # Skills for this student's role family
    primary_skills = ROLE_SKILLS.get(role_fam, ["Python","Communication","Problem Solving"])
    # Additional random skills (2-5)
    other_pool = [s for s in skills['skill_name'].tolist() if s not in primary_skills]
    extra = rng.choice(other_pool, size=int(rng.integers(2,6)), replace=False).tolist()
    all_student_skills = list(set(primary_skills + extra))

    for sk_name in all_student_skills:
        sk_id = skill_name_to_id.get(sk_name)
        if not sk_id: continue
        sk_row = skills[skills['skill_id']==sk_id].iloc[0]

        # Proficiency correlated with CGPA (r≈0.4) + role relevance bonus
        base_prof = float(np.clip(
            50 + (cgpa - 7.0)*6 + rng.normal(0, 15),
            10, 100
        ))
        if sk_name in primary_skills:
            base_prof = min(100, base_prof + 10)

        prof_score = round(float(np.clip(base_prof, 0, 100)), 1)
        prof_level = PROF_LEVELS[min(3, int(prof_score // 25))]

        # Higher proficiency → more likely to have external verification
        if prof_score >= 75:
            vsource = rng.choice(["CERTIFICATION","ASSESSMENT","PROJECT"], p=[0.4,0.35,0.25])
        elif prof_score >= 50:
            vsource = rng.choice(VERIF_SOURCES, p=[0.2,0.2,0.15,0.2,0.1,0.1,0.05])
        else:
            vsource = rng.choice(["SELF","COURSE"], p=[0.6,0.4])

        yrs_exp = round(float(np.clip(rng.exponential(1.2), 0, 5)), 1)

        stu_skill_rows.append({
            "student_id":       sid,
            "skill_id":         sk_id,
            "proficiency_score":prof_score,
            "proficiency_level":prof_level,
            "verification_source": vsource,
            "years_experience": yrs_exp,
            "last_assessed_date": str(date(2024, int(rng.integers(1,13)), int(rng.integers(1,29)))),
            "created_at":       "2024-01-01",
            "updated_at":       "2024-01-01",
        })

stu_skills_df = pd.DataFrame(stu_skill_rows)
stu_skills_df.to_csv(f"{OUT}/student_skills.csv", index=False)
print(f"  {len(stu_skills_df):,} student_skill records")

# ═══════════════════════════════════════════════════════════════════════
# 9. PROJECTS  +  STUDENT_PROJECTS  →  silver.projects / student_projects
# ═══════════════════════════════════════════════════════════════════════
print("► projects + student_projects ...")
# Real data: Projects_Count distribution: 0(3.6%) 1(11.4%) 2(18.9%) 3(19.9%) 4-5(30.8%) 6+(15%)
PROJ_TYPES    = ["ACADEMIC","PERSONAL","CAPSTONE","RESEARCH","INDUSTRY"]
PROJ_DOMAINS  = ["Web Development","Data Science","Machine Learning","Embedded Systems",
                 "Cloud","Mobile","Cybersecurity","Blockchain","IoT","Finance","Healthcare",
                 "E-Commerce","NLP","Computer Vision","Automation","Research"]
DIFF_LEVELS   = ["EASY","MEDIUM","HARD","RESEARCH"]
CONT_ROLES    = ["Lead Developer","Team Member","Data Engineer","Frontend Dev","Backend Dev","Analyst"]

proj_rows, sp_rows = [], []
proj_count_dist = [0,1,2,3,4,5,6,7,8,9,10]
proj_count_probs= [0.036,0.114,0.189,0.199,0.181,0.127,0.077,0.040,0.019,0.010,0.008]
proj_count_probs = np.array(proj_count_probs)/sum(proj_count_probs)

for i, row in students.iterrows():
    if i % 20000 == 0: print(f"   {i:,}/{N_STU:,}")
    sid  = row['student_id']
    cgpa = row['cgpa']
    n_proj = int(rng.choice(proj_count_dist, p=proj_count_probs))
    # Higher CGPA → slight more projects
    if cgpa >= 8.5 and rng.random() < 0.3: n_proj = min(10, n_proj+1)
    for j in range(n_proj):
        pid     = uid("proj", f"{sid}_{j}")
        p_type  = rng.choice(PROJ_TYPES, p=[0.35,0.25,0.20,0.10,0.10])
        domain  = rng.choice(PROJ_DOMAINS)
        diff    = rng.choice(DIFF_LEVELS, p=[0.20,0.45,0.25,0.10])
        rel_score = round(float(np.clip(rng.normal(65, 18), 10, 100)), 1)
        github  = bool(rng.random() < (0.70 if p_type=="PERSONAL" else 0.35))
        deployed= bool(rng.random() < 0.30)
        yr_end  = int(rng.integers(row['graduation_year']-3, row['graduation_year']+1))
        yr_st   = yr_end - 1
        proj_rows.append({
            "project_id":               pid,
            "project_title":            f"{domain} {p_type.title()} Project {j+1}",
            "project_type":             p_type,
            "domain":                   domain,
            "difficulty_level":         diff,
            "start_date":               str(date(yr_st, int(rng.integers(1,13)), 1)),
            "end_date":                 str(date(yr_end, int(rng.integers(1,13)), 28)),
            "industry_relevance_score": rel_score,
            "github_available":         github,
            "deployed":                 deployed,
            "created_at":               "2024-01-01",
        })
        sp_rows.append({
            "student_id":       sid,
            "project_id":       pid,
            "contribution_role":rng.choice(CONT_ROLES),
            "project_score":    round(float(np.clip(rng.normal(rel_score-5, 12), 0, 100)), 1),
            "created_at":       "2024-01-01",
        })

projects = pd.DataFrame(proj_rows).drop_duplicates('project_id')
sp_df    = pd.DataFrame(sp_rows)
projects.to_csv(f"{OUT}/projects.csv", index=False)
sp_df.to_csv(f"{OUT}/student_projects.csv", index=False)
print(f"  {len(projects):,} projects, {len(sp_df):,} student_project links")

# ═══════════════════════════════════════════════════════════════════════
# 10. INTERNSHIPS  →  silver.internships
# (Real: 0→31.7%, 1→34.6%, 2→20.9%, 3→8.7%, 4→3.0%, 5→1.1%)
# ═══════════════════════════════════════════════════════════════════════
print("► internships ...")
INT_COUNT_DIST = [0,1,2,3,4,5]
INT_COUNT_PROBS= [0.317,0.346,0.209,0.087,0.030,0.011]
DOMAINS_INT   = ["Software Development","Data Science","Machine Learning","DevOps",
                 "Product","Business Analysis","Finance","Marketing","Research","Core Engineering"]

internship_rows = []
for i, row in students.iterrows():
    if i % 20000 == 0: print(f"   {i:,}/{N_STU:,}")
    sid  = row['student_id']
    cgpa = row['cgpa']
    # Higher CGPA slightly more likely to have internships
    probs = np.array(INT_COUNT_PROBS.copy())
    if cgpa >= 8.0:
        probs[0] *= 0.6; probs = probs/probs.sum()
    n_int = int(rng.choice(INT_COUNT_DIST, p=probs))
    for j in range(n_int):
        co_id  = rng.choice(CO_IDS)
        dur    = round(float(rng.choice([1,2,3,4,5,6], p=[0.08,0.18,0.32,0.22,0.12,0.08])), 1)
        stip   = round(float(np.clip(rng.normal(15000, 8000), 3000, 80000)), 0)
        # PPO: ~15% of internships
        ppo    = bool(rng.random() < (0.20 if cgpa >= 8.0 else 0.10))
        gr_yr  = int(row['graduation_year'])
        start_yr = gr_yr - int(rng.integers(1,4))
        internship_rows.append({
            "internship_id":     uid("int", f"{sid}_{j}"),
            "student_id":        sid,
            "company_id":        co_id,
            "role_name":         rng.choice(["Software Engineering Intern","Data Science Intern",
                                             "ML Intern","Backend Intern","Research Intern",
                                             "Product Intern","Analyst Intern"]),
            "start_date":        str(date(start_yr, int(rng.integers(5,10)), 1)),
            "end_date":          str(date(start_yr, int(rng.integers(10,13)), 28)),
            "duration_months":   dur,
            "stipend_monthly":   stip,
            "domain":            rng.choice(DOMAINS_INT),
            "conversion_to_ppo": ppo,
            "ppo_offer_id":      None,
            "created_at":        "2024-01-01",
            "updated_at":        "2024-01-01",
        })

internships = pd.DataFrame(internship_rows)
internships.to_csv(f"{OUT}/internships.csv", index=False)
print(f"  {len(internships):,} internships")

# ═══════════════════════════════════════════════════════════════════════
# 11. JOB POSTINGS + JOB_POSTING_DEPARTMENTS + JOB_REQUIRED_SKILLS
# ═══════════════════════════════════════════════════════════════════════
print(f"► job_postings ({N_POST:,}) ...")
EMPL_TYPES = ["FULL_TIME","INTERNSHIP","CONTRACT","PART_TIME"]
WORK_MODES = ["ONSITE","HYBRID","REMOTE"]
POSTING_SEASONS = [(2023,8),(2023,9),(2024,8),(2024,9),(2025,8),(2025,9)]

jp_rows, jpd_rows, jrs_rows = [], [], []
role_id_list = job_roles['job_role_id'].tolist()
role_df_indexed = job_roles.set_index('job_role_id')

for i in range(N_POST):
    if i % 1000 == 0: print(f"   {i:,}/{N_POST:,}")
    co_row  = companies.iloc[i % len(companies)]
    co_id   = co_row['company_id']
    co_type = co_row['company_type']
    median_ctc = float(co_row.get('median_ctc_lpa', 8.0))

    role_id = rng.choice(role_id_list)
    role_row = job_roles[job_roles['job_role_id']==role_id].iloc[0]
    role_fam = role_row['role_family']

    # Package based on company median + noise
    pkg_med = round(float(np.clip(rng.normal(median_ctc, median_ctc*0.15), 3.0, 50.0)), 2)
    pkg_min = round(pkg_med * rng.uniform(0.7, 0.9), 2)
    pkg_max = round(pkg_med * rng.uniform(1.1, 1.4), 2)

    # CGPA cutoff: product companies stricter
    min_cgpa = float(rng.choice([6.0,6.5,7.0,7.5,8.0,8.5],
        p=[0.05,0.10,0.30,0.25,0.20,0.10] if co_type=="PRODUCT" else [0.15,0.20,0.30,0.20,0.10,0.05]))
    max_bl   = int(rng.choice([0,1,2], p=[0.40,0.40,0.20]))
    openings = int(rng.choice([1,2,3,5,10,15,20,30,50,100],
        p=[0.15,0.15,0.15,0.15,0.12,0.10,0.08,0.05,0.03,0.02]))

    season = POSTING_SEASONS[i % len(POSTING_SEASONS)]
    p_date = date(season[0], season[1], int(rng.integers(1,20)))
    d_date = p_date + timedelta(days=int(rng.integers(15,45)))
    j_date = p_date + timedelta(days=int(rng.integers(90,200)))

    jp_id = uid("jp", f"{co_id}_{i}_{SEED}")
    jp_rows.append({
        "job_posting_id":     jp_id,
        "company_id":         co_id,
        "job_role_id":        role_id,
        "job_title":          role_row['role_name'],
        "location":           rng.choice(CITIES),
        "employment_type":    "FULL_TIME",
        "work_mode":          rng.choice(WORK_MODES, p=[0.40,0.40,0.20]),
        "posting_date":       str(p_date),
        "application_deadline": str(d_date),
        "joining_date":       str(j_date),
        "min_cgpa":           min_cgpa,
        "max_backlogs":       max_bl,
        "min_percentage":     round(min_cgpa * 9.5, 1),
        "package_min_lpa":    pkg_min,
        "package_max_lpa":    pkg_max,
        "package_median_lpa": pkg_med,
        "openings":           openings,
        "is_active":          bool(p_date.year >= 2024),
        "created_at":         str(p_date),
        "updated_at":         str(p_date),
    })

    # Departments eligible for this posting
    eligible_branches = BRANCH_ROLE_AFFINITY.copy()
    eligible_depts = [d_id for d_code, d_id in zip(DEPT_CODES, DEPT_IDS)
                      if role_fam in BRANCH_ROLE_AFFINITY.get(d_code, [])]
    if not eligible_depts:
        eligible_depts = DEPT_IDS[:3]  # fallback
    for d_id in eligible_depts:
        jpd_rows.append({"job_posting_id": jp_id, "department_id": d_id, "created_at":"2024-01-01"})

    # Required skills for this posting
    req_skills = ROLE_SKILLS.get(role_fam, ["Communication","Problem Solving"])
    for sk_rank, sk_name in enumerate(req_skills):
        sk_id = skill_name_to_id.get(sk_name)
        if not sk_id: continue
        is_primary   = sk_rank < 4
        is_mandatory = sk_rank < 2
        req_score    = float(rng.uniform(60,90) if is_primary else rng.uniform(40,70))
        imp_weight   = float(rng.uniform(0.8,1.0) if is_primary else rng.uniform(0.4,0.7))
        jrs_rows.append({
            "job_posting_id":  jp_id,
            "skill_id":        sk_id,
            "required_level":  "ADVANCED" if req_score >= 75 else "INTERMEDIATE",
            "required_score":  round(req_score, 1),
            "importance_weight": round(imp_weight, 2),
            "is_mandatory":    is_mandatory,
            "created_at":      "2024-01-01",
        })

job_postings     = pd.DataFrame(jp_rows)
job_post_depts   = pd.DataFrame(jpd_rows)
job_req_skills   = pd.DataFrame(jrs_rows)
job_postings.to_csv(f"{OUT}/job_postings.csv", index=False)
job_post_depts.to_csv(f"{OUT}/job_posting_departments.csv", index=False)
job_req_skills.to_csv(f"{OUT}/job_required_skills.csv", index=False)
print(f"  {len(job_postings):,} postings, {len(job_post_depts):,} dept links, {len(job_req_skills):,} skill requirements")

# ═══════════════════════════════════════════════════════════════════════
# 12. APPLICATIONS + STATUS HISTORY  →  silver.applications
# (Real: 65.1% placed overall; CSE/IT/AIML ~83% placed)
# Correlation: DSA_r=0.39, CompProg_r=0.38, CGPA_r=0.30, Internship_r=0.28
# ═══════════════════════════════════════════════════════════════════════
print("► applications + status_history ...")
# Build lookup for skill avg per student (technical skills)
stu_tech_skill_avg = stu_skills_df[
    stu_skills_df['skill_id'].isin(
        skills[skills['skill_type'].isin(['TECHNICAL','LANGUAGE','TOOL'])]['skill_id']
    )
].groupby('student_id')['proficiency_score'].mean().to_dict()

stu_intern_count = internships.groupby('student_id').size().to_dict()

# Build student lookup dict
students_idx = students.set_index('student_id')

app_rows, hist_rows = [], []
offer_rows, placement_rows, interview_rows = [], [], []

# Only eligible/active/placed students apply
eligible_students = students[students['placement_status'].isin(['ELIGIBLE','ACTIVE','PLACED'])]
eligible_sids = set(eligible_students['student_id'].tolist())

# Sample which students apply to which postings
n_apps_target = min(len(eligible_sids) * 4, N_STU * 6)

app_count = 0
jp_indexed = job_postings.set_index('job_posting_id')
jrd_by_jp  = job_post_depts.groupby('job_posting_id')['department_id'].apply(list).to_dict()
jrs_by_jp  = job_req_skills.groupby('job_posting_id')['skill_id'].apply(list).to_dict()

ROUND_TYPES   = ["ONLINE_ASSESSMENT","TECHNICAL_1","TECHNICAL_2","MANAGERIAL","HR","FINAL"]
INT_TYPES_BY_COMPANY = {
    "PRODUCT":    ["ONLINE_ASSESSMENT","TECHNICAL_1","TECHNICAL_2","MANAGERIAL","HR"],
    "SERVICES":   ["ONLINE_ASSESSMENT","TECHNICAL_1","HR"],
    "STARTUP":    ["TECHNICAL_1","TECHNICAL_2","HR"],
    "CONSULTING": ["ONLINE_ASSESSMENT","TECHNICAL_1","MANAGERIAL","HR"],
    "BANKING":    ["ONLINE_ASSESSMENT","TECHNICAL_1","MANAGERIAL","HR"],
}

jp_list = job_postings.to_dict('records')
co_type_map = companies.set_index('company_id')['company_type'].to_dict()
co_name_map = companies.set_index('company_id')['company_name'].to_dict()

# Shuffle for variety
rng.shuffle(jp_list)

for jp in jp_list:
    jp_id    = jp['job_posting_id']
    co_id    = jp['company_id']
    min_cgpa = float(jp.get('min_cgpa',6.0))
    max_bl   = int(jp.get('max_backlogs',2))
    co_type  = co_type_map.get(co_id, "SERVICES")
    pkg_med  = float(jp.get('package_median_lpa', 8.0))
    openings = int(jp.get('openings', 5))
    eligible_dept_ids = set(jrd_by_jp.get(jp_id, DEPT_IDS))
    jp_date  = jp.get('posting_date','2024-08-01')

    # Eligible students for this posting
    pool = eligible_students[
        (eligible_students['cgpa'] >= min_cgpa) &
        (eligible_students['backlogs'] <= max_bl) &
        (eligible_students['department_id'].isin(eligible_dept_ids))
    ]
    if len(pool) == 0: continue

    # Application probability (not all eligible apply)
    attract = min(0.25, openings/200)
    base_apply = 0.22 + attract
    n_apply = int(len(pool) * rng.uniform(base_apply*0.7, base_apply*1.3))
    n_apply = max(1, min(n_apply, len(pool)))
    applicant_df = pool.sample(n=n_apply, random_state=int(rng.integers(0,99999)))

    for _, stu in applicant_df.iterrows():
        sid   = stu['student_id']
        cgpa  = float(stu['cgpa'])
        dept_id = stu['department_id']

        # Scores used for shortlist probability
        cgpa_z    = (cgpa - 7.477) / 0.871
        sk_avg    = stu_tech_skill_avg.get(sid, 50.0)
        sk_z      = (sk_avg - 55.0) / 20.0
        int_count = stu_intern_count.get(sid, 0)
        int_bonus = min(0.4, int_count * 0.12)

        # Shortlist prob — grounded in real correlations
        p_short = float(sigmoid(cgpa_z*1.2 + sk_z*0.9 + int_bonus))
        p_short = float(np.clip(p_short, 0.04, 0.88))

        # Apply
        app_id = uid("app", f"{sid}_{jp_id}")
        try:
            p_dt = date.fromisoformat(str(jp_date))
        except:
            p_dt = date(2024,8,1)
        app_date = p_dt + timedelta(days=int(rng.integers(0,20)))
        status   = "APPLIED"
        rej_reason = None
        withdrawn_dt = None

        app_hist = [{"application_id": app_id, "status":"APPLIED",
                     "status_timestamp": str(datetime.combine(app_date, datetime.min.time()))}]

        # Withdrawal (5%)
        if rng.random() < 0.05:
            status = "WITHDRAWN"
            withdrawn_dt = str(app_date + timedelta(days=int(rng.integers(1,15))))
            app_hist.append({"application_id":app_id,"status":"WITHDRAWN","status_timestamp":str(withdrawn_dt)})
        elif rng.random() < p_short:
            status = "SHORTLISTED"
            sl_date = app_date + timedelta(days=int(rng.integers(7,25)))
            app_hist.append({"application_id":app_id,"status":"SHORTLISTED","status_timestamp":str(sl_date)})

            # Interview (72% of shortlisted)
            if rng.random() < 0.72:
                status = "INTERVIEW"
                iv_date = sl_date + timedelta(days=int(rng.integers(3,14)))
                app_hist.append({"application_id":app_id,"status":"INTERVIEW","status_timestamp":str(iv_date)})

                # Generate interview rounds
                rounds = INT_TYPES_BY_COMPANY.get(co_type, ["ONLINE_ASSESSMENT","TECHNICAL_1","HR"])
                n_rounds = min(len(rounds), int(rng.integers(1, len(rounds)+1)))
                selected_rounds = rounds[:n_rounds]
                passed_all = True
                for r_num, rtype in enumerate(selected_rounds, 1):
                    tech_score = float(np.clip(rng.normal(sk_avg*0.65 + cgpa*5, 12), 0, 100))
                    comm_score = float(np.clip(rng.normal(52 + cgpa_z*5, 13), 0, 100))
                    ps_score   = float(np.clip(rng.normal(50 + cgpa_z*7, 14), 0, 100))
                    overall    = round(tech_score*0.5 + comm_score*0.25 + ps_score*0.25, 1)
                    # Pass threshold: ~65
                    result     = "PASS" if overall >= float(rng.normal(62, 6)) else "FAIL"
                    if result == "FAIL": passed_all = False

                    sched_at = iv_date + timedelta(days=r_num*3)
                    comp_at  = sched_at + timedelta(hours=int(rng.integers(1,4)))
                    interview_rows.append({
                        "interview_id":        uid("iv", f"{app_id}_{r_num}"),
                        "application_id":      app_id,
                        "round_number":        r_num,
                        "round_type":          rtype,
                        "scheduled_at":        str(sched_at),
                        "completed_at":        str(comp_at),
                        "result":              result,
                        "technical_score":     round(tech_score, 1),
                        "communication_score": round(comm_score, 1),
                        "problem_solving_score": round(ps_score, 1),
                        "overall_score":       overall,
                        "feedback":            f"Round {r_num} feedback",
                        "interviewer_type":    "INTERNAL",
                        "created_at":          str(sched_at),
                    })
                    if result == "FAIL": break

                # Offer (if passed all rounds)
                if passed_all:
                    selectivity = {"PRODUCT":0.55,"SERVICES":0.85,"STARTUP":0.70,
                                   "CONSULTING":0.72,"BANKING":0.65}.get(co_type, 0.75)
                    p_offer = float(sigmoid((overall/100 - 0.55)*5)) * selectivity
                    if rng.random() < p_offer:
                        status = "OFFERED"
                        off_date = iv_date + timedelta(days=int(rng.integers(7,21)))
                        app_hist.append({"application_id":app_id,"status":"OFFERED","status_timestamp":str(off_date)})

                        ctc = round(float(np.clip(
                            rng.normal(pkg_med, pkg_med*0.12), pkg_med*0.7, pkg_med*1.6
                        )), 2)
                        base_lpa   = round(ctc * rng.uniform(0.65,0.78), 2)
                        var_lpa    = round(ctc * rng.uniform(0.10,0.20), 2)
                        bonus_lpa  = round(ctc - base_lpa - var_lpa, 2)
                        join_dt    = str(date.fromisoformat(str(jp.get('joining_date','2025-07-01'))))

                        offer_id   = uid("off", f"{app_id}")
                        # Accept (82%)
                        if rng.random() < 0.82:
                            off_status = "ACCEPTED"
                            status     = "ACCEPTED"
                            acc_date   = off_date + timedelta(days=int(rng.integers(1,7)))
                            app_hist.append({"application_id":app_id,"status":"ACCEPTED","status_timestamp":str(acc_date)})

                            placement_rows.append({
                                "placement_id":     uid("plc", app_id),
                                "student_id":       sid,
                                "company_id":       co_id,
                                "job_posting_id":   jp_id,
                                "offer_id":         offer_id,
                                "placement_date":   str(acc_date),
                                "joining_date":     join_dt,
                                "role_name":        jp['job_title'],
                                "ctc_lpa":          ctc,
                                "placement_type":   rng.choice(["FULL_TIME","INTERNSHIP_TO_FULL_TIME","PRE_PLACEMENT_OFFER"],p=[0.70,0.20,0.10]),
                                "placement_status": "CONFIRMED",
                                "created_at":       str(acc_date),
                                "updated_at":       str(acc_date),
                            })
                        else:
                            off_status = "DECLINED"
                            status     = "DECLINED"

                        offer_rows.append({
                            "offer_id":         offer_id,
                            "application_id":   app_id,
                            "student_id":       sid,
                            "company_id":       co_id,
                            "job_posting_id":   jp_id,
                            "offer_date":       str(off_date),
                            "joining_date":     join_dt,
                            "ctc_lpa":          ctc,
                            "base_lpa":         base_lpa,
                            "variable_lpa":     var_lpa,
                            "bonus_lpa":        max(0, bonus_lpa),
                            "offer_status":     off_status,
                            "accepted_date":    str(off_date + timedelta(days=3)) if off_status=="ACCEPTED" else None,
                            "created_at":       str(off_date),
                            "updated_at":       str(off_date),
                        })
                else:
                    rej_reason = "Interview not cleared"
                    status = "REJECTED"
            else:
                rej_reason = "Not selected post shortlist"
                status = "REJECTED"
        else:
            rej_reason = "Not shortlisted"
            status = "REJECTED"

        app_rows.append({
            "application_id":     app_id,
            "student_id":         sid,
            "job_posting_id":     jp_id,
            "application_date":   str(app_date),
            "application_status": status,
            "withdrawn_date":     withdrawn_dt,
            "rejection_reason":   rej_reason,
            "source":             rng.choice(["CAMPUS_PORTAL","DIRECT","REFERRAL","EMAIL"],p=[0.65,0.18,0.12,0.05]),
            "created_at":         str(app_date),
            "updated_at":         str(app_date),
        })
        hist_rows.extend(app_hist)
        app_count += 1
        if app_count % 50000 == 0: print(f"   {app_count:,} applications so far ...")

applications  = pd.DataFrame(app_rows)
app_status_hist = pd.DataFrame(hist_rows)
offers_df       = pd.DataFrame(offer_rows)
placements_df   = pd.DataFrame(placement_rows)
interviews_df   = pd.DataFrame(interview_rows)

applications.to_csv(f"{OUT}/applications.csv", index=False)
app_status_hist.to_csv(f"{OUT}/application_status_history.csv", index=False)
offers_df.to_csv(f"{OUT}/offers.csv", index=False)
placements_df.to_csv(f"{OUT}/placements.csv", index=False)
interviews_df.to_csv(f"{OUT}/interviews.csv", index=False)
print(f"  {len(applications):,} applications")
print(f"  {len(interviews_df):,} interview rounds")
print(f"  {len(offers_df):,} offers")
print(f"  {len(placements_df):,} placements")

# ═══════════════════════════════════════════════════════════════════════
# 13. STUDENT CERTIFICATIONS + COURSES
# (Real: Certifications_Count distribution: 0(3.9%) 1(12%) 2(18.3%) 3(20%) …)
# ═══════════════════════════════════════════════════════════════════════
print("► student_certifications + student_courses ...")
CERT_NAMES = [
    ("AWS Certified Solutions Architect","AWS","Cloud"),
    ("Google Cloud Professional Data Engineer","GCP","Cloud"),
    ("Azure Data Engineer Associate","Azure","Cloud"),
    ("Certified Kubernetes Administrator","CNCF","DevOps"),
    ("TensorFlow Developer Certificate","Google","ML/AI"),
    ("Meta Front-End Developer","Meta","Frontend"),
    ("IBM Data Science Professional","IBM","Data Science"),
    ("Oracle Java SE Programmer","Oracle","Programming"),
    ("Databricks Certified Associate Developer","Databricks","Big Data"),
    ("Certified Data Professional","ICCP","Data"),
    ("Scrum Master Certification","Scrum Alliance","Management"),
    ("CompTIA Security+","CompTIA","Cybersecurity"),
    ("HackerRank Python","HackerRank","Programming"),
    ("Coursera Deep Learning Specialization","Coursera/deeplearning.ai","ML/AI"),
    ("NPTEL Data Structures","NPTEL","CS Fundamentals"),
]
COURSE_NAMES = [
    ("Machine Learning by Andrew Ng","Coursera","ML/AI"),
    ("Data Structures and Algorithms","Udemy","CS Fundamentals"),
    ("Full Stack Web Development","Udemy","Web"),
    ("Deep Learning Specialization","Coursera","ML/AI"),
    ("The Complete SQL Bootcamp","Udemy","Database"),
    ("React - The Complete Guide","Udemy","Frontend"),
    ("Python for Data Science","edX","Data Science"),
    ("System Design Interview","Grokking","Software Engineering"),
    ("AWS Cloud Practitioner Essentials","AWS","Cloud"),
    ("Spark and Python for Big Data","Udemy","Big Data"),
    ("Introduction to NLP","Coursera","ML/AI"),
    ("Statistics for Data Science","edX","Analytics"),
    ("DevOps Fundamentals","LinkedIn Learning","DevOps"),
    ("DBMS and SQL","NPTEL","Database"),
    ("Operating Systems","NPTEL","CS Fundamentals"),
]

CERT_COUNT_DIST  = [0,1,2,3,4,5,6,7,8,9,10]
CERT_COUNT_PROBS = [0.039,0.120,0.183,0.200,0.179,0.124,0.075,0.044,0.021,0.010,0.005]
CERT_COUNT_PROBS = np.array(CERT_COUNT_PROBS)/sum(CERT_COUNT_PROBS)

cert_rows, course_rows = [], []
for i, row in students.iterrows():
    sid  = row['student_id']
    cgpa = row['cgpa']
    n_cert = int(rng.choice(CERT_COUNT_DIST, p=CERT_COUNT_PROBS))
    if cgpa >= 8.0 and rng.random() < 0.3: n_cert = min(10, n_cert+1)
    chosen_certs = rng.choice(len(CERT_NAMES), size=min(n_cert, len(CERT_NAMES)), replace=False)
    for ci in chosen_certs:
        cn, issuer, dom = CERT_NAMES[ci]
        yr = int(rng.integers(row['graduation_year']-3, row['graduation_year']+1))
        cert_rows.append({
            "certification_id":   uid("cert", f"{sid}_{ci}"),
            "student_id":         sid,
            "certification_name": cn,
            "issuing_organization": issuer,
            "domain":             dom,
            "issue_date":         str(date(yr, int(rng.integers(1,13)), 1)),
            "expiry_date":        str(date(yr+3, int(rng.integers(1,13)), 1)),
            "credential_id":      f"CRED-{sid[:6]}-{ci}",
            "is_valid":           True,
            "created_at":         "2024-01-01",
        })
    # Courses (1-5 per student)
    n_courses = int(rng.integers(1, 6))
    chosen_courses = rng.choice(len(COURSE_NAMES), size=min(n_courses, len(COURSE_NAMES)), replace=False)
    for cri in chosen_courses:
        cn, platform, dom = COURSE_NAMES[cri]
        yr = int(rng.integers(row['graduation_year']-3, row['graduation_year']+1))
        course_rows.append({
            "course_id":       uid("crs", f"{sid}_{cri}"),
            "student_id":      sid,
            "course_name":     cn,
            "platform":        platform,
            "domain":          dom,
            "completion_date": str(date(yr, int(rng.integers(1,13)), 1)),
            "grade":           rng.choice(["A","B","C","Pass","Distinction"],p=[0.25,0.30,0.20,0.15,0.10]),
            "is_completed":    True,
            "created_at":      "2024-01-01",
        })

cert_df   = pd.DataFrame(cert_rows)
course_df = pd.DataFrame(course_rows)
cert_df.to_csv(f"{OUT}/student_certifications.csv", index=False)
course_df.to_csv(f"{OUT}/student_courses.csv", index=False)
print(f"  {len(cert_df):,} certifications, {len(course_df):,} courses")

# ═══════════════════════════════════════════════════════════════════════
# 14. PLACEMENT EVENTS  →  silver.placement_events
# ═══════════════════════════════════════════════════════════════════════
print("► placement_events ...")
EVENT_TYPES = ["CAMPUS_DRIVE","PRE_PLACEMENT_TALK","HACKATHON","CODING_TEST","SEMINAR","WORKSHOP","JOB_FAIR"]
event_rows = []
unique_companies = companies.sample(min(100, len(companies)), random_state=SEED)
for i, co_row in unique_companies.iterrows():
    n_events = int(rng.integers(1,4))
    for j in range(n_events):
        ev_date = date(rng.choice([2023,2024,2025]), int(rng.integers(7,12)), int(rng.integers(1,28)))
        event_rows.append({
            "event_id":    uid("ev", f"{co_row['company_id']}_{j}"),
            "company_id":  co_row['company_id'],
            "event_name":  f"{co_row['company_name']} {rng.choice(EVENT_TYPES)}",
            "event_type":  rng.choice(EVENT_TYPES),
            "event_date":  str(ev_date),
            "venue":       rng.choice(["Main Auditorium","Seminar Hall","Online","Conference Room A","LH1"]),
            "description": f"Placement event by {co_row['company_name']}",
            "is_active":   True,
            "created_at":  "2024-01-01",
        })
placement_events_df = pd.DataFrame(event_rows)
placement_events_df.to_csv(f"{OUT}/placement_events.csv", index=False)
print(f"  {len(placement_events_df):,} placement events")

# ═══════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print(" GENERATION COMPLETE")
print(f"{'='*60}")
generated = {}
import os
for fname in sorted(os.listdir(OUT)):
    if fname.endswith('.csv'):
        fpath = os.path.join(OUT, fname)
        n = sum(1 for _ in open(fpath)) - 1
        sz = os.path.getsize(fpath)
        generated[fname] = (n, sz)
        print(f"  {fname:<50} {n:>10,} rows  {sz/1024/1024:6.1f} MB")

print(f"\n  Output dir: {OUT}/")
print(f"  Total files: {len(generated)}")
total_rows = sum(v[0] for v in generated.values())
total_mb   = sum(v[1] for v in generated.values()) / 1024/1024
print(f"  Total rows:  {total_rows:,}")
print(f"  Total size:  {total_mb:.1f} MB")

# Funnel validation
n_apps   = len(applications)
n_short  = (applications['application_status'].isin(['SHORTLISTED','INTERVIEW','OFFERED','ACCEPTED'])).sum()
n_iv     = (applications['application_status'].isin(['INTERVIEW','OFFERED','ACCEPTED'])).sum()
n_off    = len(offers_df)
n_placed = len(placements_df)
print(f"\n FUNNEL CHECK:")
print(f"  Applications: {n_apps:,}")
print(f"  Shortlisted:  {n_short:,}  ({n_short/n_apps*100:.1f}%)")
print(f"  Interviewed:  {n_iv:,}  ({n_iv/n_apps*100:.1f}%)")
print(f"  Offered:      {n_off:,}  ({n_off/n_apps*100:.1f}%)")
print(f"  Placed:       {n_placed:,}  ({n_placed/n_apps*100:.1f}%)")
print()
