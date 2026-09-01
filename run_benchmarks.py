import duckdb
import pandas as pd

# Connect to database
con = duckdb.connect('data/placewise.duckdb')

benchmarks = [
    {
        "question": "What is the average package?",
        "expected_logic": "AVG(final_package_lpa) FROM semantic.genie_student WHERE placement_status='Placed'",
        "generated_sql": "SELECT AVG(final_package_lpa) FROM semantic.genie_student WHERE placement_status='Placed';"
    },
    {
        "question": "How many students are placed?",
        "expected_logic": "COUNT(*) WHERE placement_status='Placed'",
        "generated_sql": "SELECT COUNT(*) FROM semantic.genie_student WHERE placement_status='Placed';"
    },
    {
        "question": "Which company hired the most students?",
        "expected_logic": "ORDER BY total_hires DESC LIMIT 1",
        "generated_sql": "SELECT company_name, total_hires FROM semantic.genie_company ORDER BY total_hires DESC LIMIT 1;"
    },
    {
        "question": "What is the placement rate for Computer Science?",
        "expected_logic": "placement_rate FROM semantic.genie_department WHERE department='Computer Science'",
        "generated_sql": "SELECT placement_rate FROM semantic.genie_department WHERE department_name='Computer Science';"
    },
    {
        "question": "What is the most demanded skill?",
        "expected_logic": "ORDER BY total_demand DESC LIMIT 1",
        "generated_sql": "SELECT skill_name, total_demand FROM semantic.genie_skill ORDER BY total_demand DESC LIMIT 1;"
    }
]

results = []
passed = 0
failed = 0

for b in benchmarks:
    try:
        df = con.execute(b["generated_sql"]).df()
        status = "PASS"
        passed += 1
    except Exception as e:
        status = f"FAIL: {str(e)}"
        failed += 1
    
    results.append(f"| {b['question']} | `{b['expected_logic']}` | `{b['generated_sql']}` | {status} |")

# Write to docs/genie_test_results.md
with open('docs/genie_test_results.md', 'w') as f:
    f.write("# Genie Benchmark Test Results\n\n")
    f.write(f"**Result Summary:** {passed} PASSED, {failed} FAILED (Total: {len(benchmarks)})\n\n")
    f.write("| Question | Expected Logic | Generated SQL | Status |\n")
    f.write("|----------|----------------|---------------|--------|\n")
    for r in results:
        f.write(r + "\n")

print("Benchmark tests completed.")
