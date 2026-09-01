# Data Quality Framework

## Overview
Placewise implements data quality checks primarily during the Bronze-to-Silver transition using dbt constraints and custom tests.

## Severity Levels
- **INFO**: Minor anomalies for reporting only. (e.g., `email` domain is unusual).
- **WARNING**: Data might be slightly off but usable. Record proceeds to Silver. (e.g., `cgpa` > 10.0, cap to 10.0).
- **ERROR**: Critical data missing. Record quarantined. (e.g., `student_id` is null).
- **CRITICAL**: Systematic failure. Abort pipeline. (e.g., 100% of packages are null).

## Checks per Table (Examples)

### `silver_students`
- `student_id`: NOT NULL (ERROR), UNIQUE (ERROR)
- `cgpa`: BETWEEN 0 and 10 (WARNING - clip to bounds)
- `department_id`: IN list of valid departments (ERROR)

### `silver_placements`
- `final_package_lpa`: > 0 (ERROR), < 100 (WARNING)
- `offer_date`: >= `application_date` (ERROR)

## Quarantine Strategy
Records failing ERROR-level checks are written to a `quarantine` schema (`silver_students_quarantine`) along with a `dq_error_message` column. The main Silver table only receives clean records. This prevents dashboard outages while alerting data stewards.

## DQ Report Table Schema
| Column | Type | Description |
|---|---|---|
| `run_id` | STRING | dbt invocation ID |
| `table_name` | STRING | Name of tested table |
| `test_name` | STRING | Rule violated |
| `severity` | STRING | INFO/WARNING/ERROR |
| `records_failed`| INT | Number of violating rows |

## Action Plan for Failures
1. Data stewards monitor the `gold_dq_dashboard`.
2. For quarantined records, fix at the source system (e.g., update student portal).
3. Pipeline automatically re-ingests and clears quarantine on next run.
