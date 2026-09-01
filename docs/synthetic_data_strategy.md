# Synthetic Data Strategy

## Overview
To develop and test Placewise pipelines and Genie spaces before real data is available, we generate highly correlated synthetic data using Python (`faker`, `pandas`, `numpy`).

## Correlation Model
The generator builds realistic relationships rather than purely random data:
- `cgpa` is normally distributed (mean=7.5, std=1.0).
- `package_lpa` has a strong positive correlation with `cgpa` and `company_tier`. (e.g., Tier 1 companies require CGPA > 8.0 and offer > 15 LPA).
- `interview_score` correlates with `placement_readiness_score`.
- `placement_status` probability increases significantly with higher `placement_readiness_score`.

## Generation Order & Dependency Graph
Data must be generated hierarchically to maintain referential integrity:
1. Departments
2. Companies -> Job Postings
3. Students -> Student Skills
4. Applications -> Interviews -> Placements

## Profile System
- **Small**: 500 students, 20 companies (for local unit testing)
- **Medium**: 2000 students, 100 companies (for integration testing)
- **Large**: 10000 students, 300 companies (for load testing and Genie demo)

## Real Data Augmentation Workflow
When partial real data arrives:
1. Load real entity (e.g., Real Students).
2. Use the real `student_id` and `cgpa` as seeds for the generator.
3. Generate synthetic Applications, Interviews, and Placements linked to those real students, respecting the real `cgpa` distribution.

## Validation Approach
After generation, `great_expectations` runs against the CSVs to ensure:
- No orphan records (foreign keys valid).
- Placed students have at least one Application and 'Pass' Interview.
- Final package is within the Job Posting's stated range.

## Limitations
- Lacks natural text variability in resume text or interview feedback notes.
- Perfect enforcement of rules (e.g., no student with CGPA < min_required ever applies) which doesn't reflect real-world anomalies.
