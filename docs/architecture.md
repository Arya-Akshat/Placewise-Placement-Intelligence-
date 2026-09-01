# Architecture

## Overview
Placewise utilizes a Medallion Architecture on Databricks Unity Catalog, implemented primarily via dbt. Data flows from raw files (CSV/JSON) into Bronze, is cleansed into Silver, aggregated into Gold, and finally exposed via a Semantic layer tailored for Databricks Genie.

## Medallion Architecture
- **Bronze:** Raw, ingested data with minimal schema enforcement. Append-only or full overwrite depending on source.
- **Silver:** Cleansed, conformed dimensions and facts. Enforces data types, constraints, and relationships.
- **Gold:** Business-level aggregates (e.g., department performance, company hiring trends).
- **Semantic:** Flattened, user-friendly views designed specifically for Genie natural language querying.

## Data Lineage

```mermaid
graph LR
    subgraph Sources
    S1[Student Portal CSV]
    S2[Company Forms JSON]
    S3[Interview ATS API]
    end

    subgraph Bronze
    B1[bronze_students]
    B2[bronze_companies]
    B3[bronze_interviews]
    end

    subgraph Silver
    Si1[silver_students]
    Si2[silver_companies]
    Si3[silver_interviews]
    Si4[silver_placements]
    end

    subgraph Gold
    G1[gold_department_metrics]
    G2[gold_company_metrics]
    G3[gold_student_metrics]
    end

    subgraph Semantic
    Sem1[semantic_student_placement]
    Sem2[semantic_company_hiring]
    end

    S1 --> B1
    S2 --> B2
    S3 --> B3

    B1 --> Si1
    B2 --> Si2
    B3 --> Si3

    Si1 & Si2 & Si3 --> Si4

    Si1 & Si4 --> G1
    Si2 & Si4 --> G2
    Si1 & Si2 & Si3 & Si4 --> G3

    G1 & G2 & G3 & Si1 & Si2 --> Sem1
    G2 & Si2 & Si4 --> Sem2

    Sem1 & Sem2 --> Genie[Databricks Genie]
```

## Entity-Relationship Diagram (Silver Layer)

```mermaid
erDiagram
    silver_students ||--o{ silver_applications : makes
    silver_students ||--o{ silver_placements : achieves
    silver_students ||--o{ silver_student_skills : possesses
    silver_companies ||--o{ silver_job_postings : posts
    silver_job_postings ||--o{ silver_applications : receives
    silver_applications ||--o{ silver_interviews : triggers
    silver_interviews ||--o| silver_placements : results_in
    silver_job_postings ||--o{ silver_job_skills : requires
```

## Key Design Decisions
1. **Bridge Tables for Skills/Departments:** `job_posting_departments` is a bridge table rather than an array column in `job_postings` to simplify Genie querying and standard SQL joins. Array explosion is often difficult for LLM-based query generation.
2. **Semantic Layer Flattening:** The Semantic layer deliberately denormalizes certain Gold/Silver tables to avoid Genie having to infer complex join paths across 5+ tables.
3. **Data Quality Quarantine:** Bad records in Silver load are routed to a quarantine table (`silver_quarantine`) rather than failing the pipeline, ensuring partial data availability.

## Deployment Notes
- Unity Catalog is required.
- Schemas: `placewise_bronze`, `placewise_silver`, `placewise_gold`, `placewise_semantic`.

## Assumptions
- Student IDs and Company IDs are persistent across academic years.
- Package values are strictly in LPA (Lakhs Per Annum) for consistency.
