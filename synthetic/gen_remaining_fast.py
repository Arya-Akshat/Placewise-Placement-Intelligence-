"""Fast generator for certifications, courses, placement_events."""
import os, sys, hashlib
import numpy as np
import pandas as pd
from datetime import date

OUT  = sys.argv[1] if len(sys.argv) > 1 else 'data/synthetic'
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 42
rng  = np.random.default_rng(SEED)

def uid(prefix, key):
    return f"{prefix}_{hashlib.md5(str(key).encode()).hexdigest()[:10]}"

students  = pd.read_csv(f"{OUT}/students.csv")
companies = pd.read_csv(f"{OUT}/companies.csv")
N = len(students)
print(f"Generating remaining tables for {N:,} students...")

# ── Certifications ──────────────────────────────────────────────────────
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
    ("Scrum Master Certification","Scrum Alliance","Management"),
    ("CompTIA Security+","CompTIA","Cybersecurity"),
    ("HackerRank Python","HackerRank","Programming"),
    ("Coursera Deep Learning Specialization","Coursera","ML/AI"),
    ("NPTEL Data Structures","NPTEL","CS Fundamentals"),
    ("Microsoft Azure Fundamentals","Microsoft","Cloud"),
]
# Real distribution from Kaggle profiling
cert_count_probs = np.array([0.039,0.120,0.183,0.200,0.179,0.124,0.075,0.044,0.021,0.010,0.005])
cert_count_probs /= cert_count_probs.sum()
cert_counts = rng.choice(np.arange(len(cert_count_probs)), size=N, p=cert_count_probs)

cert_rows = []
for i, row in students.iterrows():
    sid  = row['student_id']
    grad = int(row['graduation_year'])
    n_c  = int(cert_counts[i])
    chosen = rng.choice(len(CERT_NAMES), size=min(n_c, len(CERT_NAMES)), replace=False)
    for ci in chosen:
        cn, issuer, dom = CERT_NAMES[ci]
        yr = max(2018, min(grad, int(rng.integers(grad-3, grad+1))))
        cert_rows.append({
            "certification_id":     uid("cert", f"{sid}_{ci}"),
            "student_id":           sid,
            "certification_name":   cn,
            "issuing_organization": issuer,
            "domain":               dom,
            "issue_date":           str(date(yr, int(rng.integers(1,13)), 1)),
            "expiry_date":          str(date(yr+3, int(rng.integers(1,13)), 1)),
            "credential_id":        f"CRED-{sid[:6]}-{ci}",
            "is_valid":             True,
            "created_at":           "2024-01-01",
        })
pd.DataFrame(cert_rows).to_csv(f"{OUT}/student_certifications.csv", index=False)
print(f"  student_certifications: {len(cert_rows):,}")

# ── Courses ─────────────────────────────────────────────────────────────
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
course_rows = []
n_courses_arr = rng.integers(1, 6, size=N)
for i, row in students.iterrows():
    sid  = row['student_id']
    grad = int(row['graduation_year'])
    chosen = rng.choice(len(COURSE_NAMES), size=min(int(n_courses_arr[i]), len(COURSE_NAMES)), replace=False)
    for ci in chosen:
        cn, platform, dom = COURSE_NAMES[ci]
        yr = max(2018, min(grad, int(rng.integers(grad-3, grad+1))))
        course_rows.append({
            "course_id":       uid("crs", f"{sid}_{ci}"),
            "student_id":      sid,
            "course_name":     cn,
            "platform":        platform,
            "domain":          dom,
            "completion_date": str(date(yr, int(rng.integers(1,13)), 1)),
            "grade":           rng.choice(["A","B","C","Pass","Distinction"], p=[0.25,0.30,0.20,0.15,0.10]),
            "is_completed":    True,
            "created_at":      "2024-01-01",
        })
pd.DataFrame(course_rows).to_csv(f"{OUT}/student_courses.csv", index=False)
print(f"  student_courses:        {len(course_rows):,}")

# ── Placement Events ─────────────────────────────────────────────────────
EVENT_TYPES = ["CAMPUS_DRIVE","PRE_PLACEMENT_TALK","HACKATHON","CODING_TEST","SEMINAR","WORKSHOP","JOB_FAIR"]
VENUES = ["Main Auditorium","Seminar Hall A","Seminar Hall B","Online","Conference Room","LH1","LH2"]
event_rows = []
sample_cos = companies.sample(min(150, len(companies)), random_state=SEED)
for _, co in sample_cos.iterrows():
    for j in range(int(rng.integers(1,4))):
        ev_date = date(rng.choice([2023,2024,2025]), int(rng.integers(7,12)), int(rng.integers(1,28)))
        ev_type = rng.choice(EVENT_TYPES)
        event_rows.append({
            "event_id":    uid("ev", f"{co['company_id']}_{j}"),
            "company_id":  co['company_id'],
            "event_name":  f"{co['company_name']} {ev_type.replace('_',' ').title()}",
            "event_type":  ev_type,
            "event_date":  str(ev_date),
            "venue":       rng.choice(VENUES),
            "description": f"Placement drive/event organised by {co['company_name']}",
            "is_active":   True,
            "created_at":  "2024-01-01",
        })
pd.DataFrame(event_rows).to_csv(f"{OUT}/placement_events.csv", index=False)
print(f"  placement_events:       {len(event_rows):,}")

# ── Final summary ────────────────────────────────────────────────────────
print("\nAll remaining tables written.")
