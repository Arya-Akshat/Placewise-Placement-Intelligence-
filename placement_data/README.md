# Indian Engineering Students: Placement & Career Readiness Dataset (2026)

> **15,000 synthetic engineering student records designed for Exploratory Data Analysis (EDA), Machine Learning, and Educational Analytics.**

---

## Overview

Engineering placements remain one of the most important milestones for students across India. Factors such as academic performance, technical skills, internships, communication abilities, and extracurricular involvement often influence placement outcomes in different ways.

The **Indian Engineering Students: Placement & Career Readiness Dataset (2026)** was created to provide a realistic and well-structured dataset that enables students, educators, and data science practitioners to explore these relationships through data.

This dataset contains **15,000 records** and **25 features**, covering multiple aspects of a student's academic and professional profile. It is intended for educational use and supports a wide range of machine learning and analytical workflows.

> **Note:** All records are synthetically generated. No real student information has been used in the creation of this dataset.

---

## Why This Dataset?

Many publicly available placement datasets are either:

* Very small in size
* Missing documentation
* Limited to a few attributes
* Difficult to use for machine learning projects
* Inconsistent in terms of data quality

This dataset was designed with the following goals in mind:

* Provide realistic placement trends.
* Support end-to-end machine learning workflows.
* Include meaningful relationships between features.
* Offer sufficient scale for EDA and model development.
* Serve as a learning resource for students and educators.

---

## Dataset Snapshot

| Metric                            |       Value |
| --------------------------------- | ----------: |
| Total Records                     |      15,000 |
| Total Features                    |          25 |
| Placement Rate                    |      65.13% |
| Average CGPA                      |        7.48 |
| Average DSA Problems Solved       |      181.76 |
| Average Internships               |        1.20 |
| Average Package (Placed Students) |   10.05 LPA |
| Missing Values                    | 480 (0.13%) |

---

## Features Included

| Category                | Examples                                        |
| ----------------------- | ----------------------------------------------- |
| Academic Performance    | CGPA, Attendance                                |
| Technical Skills        | DSA, Competitive Programming                    |
| Professional Experience | Internships, Certifications                     |
| Open Source Activity    | GitHub Contributions, Open Source Contributions |
| Soft Skills             | Communication Score, Soft Skills Score          |
| Leadership              | Leadership Experience                           |
| Extracurriculars        | Hackathons, Activities                          |
| Career Outcomes         | Placement Status, Package LPA                   |

A complete description of every column is available in `data_dictionary.md`.

---

## Included Files

```text
indian_engineering_placement_2026.csv
README.md
data_dictionary.md
dataset_statistics.md
eda_insights.md
baseline_ml_recommendations.md
```

---

## Potential Use Cases

### Exploratory Data Analysis

* Placement trends across engineering branches
* Tier-wise salary analysis
* Correlation studies
* Package distribution analysis
* Student performance comparisons

### Machine Learning

#### Classification

* Placement Prediction

#### Regression

* Salary Package Prediction

#### Clustering

* Student Segmentation
* Career Readiness Analysis

### Educational Applications

* Classroom demonstrations
* Capstone projects
* Data science assignments
* Machine learning tutorials
* Educational analytics research

---

## Statistical Characteristics

The dataset incorporates domain-informed relationships, including:

* Higher placement probabilities for students with stronger technical profiles.
* Positive relationships between internships and placement outcomes.
* Tier-wise differences in compensation.
* Branch-specific placement trends.
* Realistic package distributions.
* Exceptional student profiles representing high-performing outliers.

These relationships were intentionally incorporated to create meaningful patterns suitable for downstream analysis.

---

## Data Quality

The dataset has been validated against several quality checks:

| Validation Check                | Status |
| ------------------------------- | ------ |
| Duplicate Records               | Passed |
| Duplicate Student IDs           | Passed |
| Missing Value Analysis          | Passed |
| Package Distribution Validation | Passed |
| Branch-wise Placement Trends    | Passed |
| Tier-wise Compensation Trends   | Passed |
| Statistical Consistency Checks  | Passed |

---

## Missing Values

To support preprocessing and data cleaning exercises, minor missing values were intentionally introduced in the following columns:

| Column                    | Missing Values |
| ------------------------- | -------------: |
| Open_Source_Contributions |            255 |
| LinkedIn_Activity_Score   |            225 |

Total missing values account for approximately **0.13%** of the dataset.

---

## Suggested Workflow

1. Load and inspect the dataset.
2. Perform data cleaning and missing value handling.
3. Conduct exploratory data analysis.
4. Build baseline machine learning models.
5. Evaluate feature importance.
6. Experiment with feature engineering.
7. Compare model performance.

---

## License

This dataset is distributed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license.

---

## Citation

If you use this dataset in research, publications, or academic projects, please cite:

> Vishwajeet Chandole. *Indian Engineering Students: Placement & Career Readiness Dataset (2026).* Kaggle Dataset, 2026.

---

## Acknowledgements

This dataset was created with the intention of contributing a useful educational resource to the Kaggle community. I hope it helps students, educators, and practitioners explore engineering placement trends and build meaningful machine learning projects.

If you find this dataset useful, consider sharing your notebooks and analyses with the community.
