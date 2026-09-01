import duckdb

con = duckdb.connect('data/placewise.duckdb')

print("=== Cross-Checking Metrics: RAW vs GOLD vs SEMANTIC ===")

# 1. Placement Rate
try:
    print("\n1. Placement Rate:")
    gold_rate = con.execute("SELECT (SUM(CASE WHEN placement_status='Placed' THEN 1 ELSE 0 END)*1.0 / COUNT(*)) FROM gold.student_placement_profile").fetchone()[0]
    semantic_rate = con.execute("SELECT (SUM(CASE WHEN placement_status='Placed' THEN 1 ELSE 0 END)*1.0 / COUNT(*)) FROM semantic.genie_student").fetchone()[0]
    print(f"  Gold: {gold_rate}")
    print(f"  Semantic: {semantic_rate}")
except Exception as e:
    print(f"  Error: {e}")

# 2. Average Package
try:
    print("\n2. Average Package:")
    gold_pkg = con.execute("SELECT AVG(final_package_lpa) FROM gold.student_placement_profile WHERE placement_status='Placed'").fetchone()[0]
    semantic_pkg = con.execute("SELECT AVG(final_package_lpa) FROM semantic.genie_student WHERE placement_status='Placed'").fetchone()[0]
    print(f"  Gold: {gold_pkg}")
    print(f"  Semantic: {semantic_pkg}")
except Exception as e:
    print(f"  Error: {e}")

# 3. Interview Conversion
try:
    print("\n3. Interview Conversion:")
    gold_conv = con.execute("SELECT AVG(interview_pass_rate) FROM gold.student_placement_profile").fetchone()[0]
    print(f"  Gold: {gold_conv}")
except Exception as e:
    print(f"  Error: {e}")

# 4. Readiness
try:
    print("\n4. Readiness:")
    gold_readiness = con.execute("SELECT AVG(readiness_score) FROM gold.student_placement_profile").fetchone()[0]
    semantic_readiness = con.execute("SELECT AVG(readiness_score) FROM semantic.genie_student").fetchone()[0]
    print(f"  Gold: {gold_readiness}")
    print(f"  Semantic: {semantic_readiness}")
except Exception as e:
    print(f"  Error: {e}")

# 5. Skill Gap
try:
    print("\n5. Skill Gap:")
    gold_gap = con.execute("SELECT AVG(skill_gap_index) FROM gold.skill_demand_profile").fetchone()[0]
    semantic_gap = con.execute("SELECT AVG(skill_gap_index) FROM semantic.genie_skill").fetchone()[0]
    print(f"  Gold: {gold_gap}")
    print(f"  Semantic: {semantic_gap}")
except Exception as e:
    print(f"  Error: {e}")

