# Data Dictionary

## Silver Layer (Canonical Schema)

### `silver_students`
- **Purpose:** Core student demographics and academic information.
- **Primary Key:** `student_id`
| Column | Type | Description | Constraints | Example |
|---|---|---|---|---|
| `student_id` | STRING | Unique identifier | NOT NULL, UNIQUE | 'STU-2023-001' |
| `first_name` | STRING | Student first name | NOT NULL | 'Aarav' |
| `last_name` | STRING | Student last name | NOT NULL | 'Patel' |
| `department_id` | STRING | Foreign key to department | NOT NULL | 'DEPT-CS' |
| `graduation_year` | INT | Expected year of graduation | NOT NULL | 2024 |
| `cgpa` | DOUBLE | Cumulative GPA | 0.0 to 10.0 | 8.75 |
| `gender` | STRING | Student gender | 'M', 'F', 'O' | 'M' |
| `email` | STRING | Contact email | UNIQUE | 'aarav@edu.in' |

### `silver_companies`
- **Purpose:** Participating companies and basic details.
- **Primary Key:** `company_id`
| Column | Type | Description | Constraints | Example |
|---|---|---|---|---|
| `company_id` | STRING | Unique identifier | NOT NULL, UNIQUE | 'COMP-001' |
| `company_name` | STRING | Name of the company | NOT NULL | 'TechNova' |
| `industry` | STRING | Industry sector | NOT NULL | 'Software' |
| `tier` | STRING | Company classification tier | 'Tier 1', 'Tier 2', 'Tier 3' | 'Tier 1' |

### `silver_job_postings`
- **Purpose:** Specific job roles offered by companies during drives.
- **Primary Key:** `job_id`
| Column | Type | Description | Constraints | Example |
|---|---|---|---|---|
| `job_id` | STRING | Unique identifier | NOT NULL, UNIQUE | 'JOB-101' |
| `company_id` | STRING | Foreign key to company | NOT NULL | 'COMP-001' |
| `role_title` | STRING | Job title | NOT NULL | 'Software Engineer' |
| `base_package_lpa` | DOUBLE | Base salary offered | >= 0 | 12.5 |
| `min_cgpa_required` | DOUBLE | Eligibility criteria | 0.0 to 10.0 | 7.5 |

### `silver_applications`
- **Purpose:** Record of students applying to specific jobs.
- **Primary Key:** `application_id`
| Column | Type | Description | Constraints | Example |
|---|---|---|---|---|
| `application_id` | STRING | Unique identifier | NOT NULL, UNIQUE | 'APP-5001' |
| `student_id` | STRING | Foreign key to student | NOT NULL | 'STU-2023-001' |
| `job_id` | STRING | Foreign key to job | NOT NULL | 'JOB-101' |
| `application_date` | DATE | Date applied | <= CURRENT_DATE | '2023-09-15' |
| `status` | STRING | Current status | 'Applied', 'Shortlisted', 'Rejected', 'Selected' | 'Shortlisted' |

### `silver_interviews`
- **Purpose:** Details of interview rounds.
- **Primary Key:** `interview_id`
| Column | Type | Description | Constraints | Example |
|---|---|---|---|---|
| `interview_id` | STRING | Unique identifier | NOT NULL, UNIQUE | 'INT-801' |
| `application_id` | STRING | Foreign key to application | NOT NULL | 'APP-5001' |
| `round_number` | INT | Sequence of round | >= 1 | 1 |
| `interview_type` | STRING | Type of round | 'Technical', 'HR', 'Aptitude' | 'Technical' |
| `score` | DOUBLE | Assessment score | 0.0 to 100.0 | 85.0 |
| `result` | STRING | Outcome | 'Pass', 'Fail' | 'Pass' |

### `silver_placements`
- **Purpose:** Final confirmed job offers accepted by students.
- **Primary Key:** `placement_id`
| Column | Type | Description | Constraints | Example |
|---|---|---|---|---|
| `placement_id` | STRING | Unique identifier | NOT NULL, UNIQUE | 'PLC-301' |
| `student_id` | STRING | Foreign key to student | NOT NULL | 'STU-2023-001' |
| `job_id` | STRING | Foreign key to job | NOT NULL | 'JOB-101' |
| `final_package_lpa`| DOUBLE | Final accepted package | >= 0 | 14.0 |
| `offer_date` | DATE | Date offer made/accepted | NOT NULL | '2023-11-20' |

## Gold Layer

### `gold_department_metrics`
- **Purpose:** Aggregated placement stats by department and year.
- **Primary Key:** (`department_id`, `graduation_year`)
| Column | Type | Description |
|---|---|---|
| `department_id` | STRING | Department ID |
| `graduation_year` | INT | Cohort year |
| `total_students` | INT | Count of eligible students |
| `placed_students` | INT | Count of students with at least 1 placement |
| `avg_package_lpa` | DOUBLE | Average package for placed students |

### `gold_student_metrics`
- **Purpose:** Individual student performance and funnel metrics.
- **Primary Key:** `student_id`
| Column | Type | Description |
|---|---|---|
| `student_id` | STRING | Student ID |
| `total_applications`| INT | Number of jobs applied to |
| `interviews_attended`| INT | Number of interview rounds attended |
| `offers_received` | INT | Number of final offers |
| `placement_status` | STRING | 'Placed' or 'Unplaced' |
