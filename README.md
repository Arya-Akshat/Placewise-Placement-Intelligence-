# Placewise — AI-Powered Campus Placement Intelligence

Placewise is an AI-powered campus placement intelligence platform built on Databricks. It provides end-to-end data pipelines, a Medallion architecture, and semantic layer integration for Databricks Genie, enabling natural language querying of placement data.

## Key Capabilities
- **Automated Data Ingestion:** Process student profiles, academic records, company requirements, and placement drives.
- **Medallion Architecture:** Bronze (raw), Silver (cleansed, conformed), and Gold (business-level aggregates) tables.
- **Semantic Layer for Genie:** Pre-configured views and metrics for accurate natural language BI.
- **Synthetic Data Generation:** Configurable generator for testing and demonstration with realistic correlations (e.g., high CGPA -> higher package).
- **Data Quality Framework:** Built-in validation rules and quarantine logic.

## Tech Stack
- **Databricks:** SQL Warehouses, Workflows, Genie, Unity Catalog
- **dbt (Databricks SQL):** Data transformation and modeling (Silver/Gold/Semantic)
- **Python (PySpark/Pandas):** Synthetic data generation and orchestration
- **Mermaid:** Architecture and ER diagrams

## Repository Structure
```
.
├── README.md                           # This file
├── docs/                               # Documentation
│   ├── architecture.md                 # System architecture and data lineage
│   ├── data_dictionary.md              # Table and column definitions
│   ├── data_quality.md                 # Validation rules and quarantine strategy
│   ├── genie_semantics.md              # Semantic layer setup for Databricks Genie
│   ├── metric_definitions.md           # Business metrics and SQL formulas
│   ├── question_traceability.md        # Genie question to SQL mapping
│   └── synthetic_data_strategy.md      # Data generation approach
├── dbt_project/                        # dbt models for Bronze -> Silver -> Gold -> Semantic
├── scripts/
│   └── generate_synthetic_data.py      # Python synthetic data generator
└── tests/                              # Unit and integration tests
```

## Quick Start
1. **Clone the repository:** `git clone <repo_url>`
2. **Setup Databricks CLI:** Configure your `.databrickscfg` with host and token.
3. **Run Synthetic Data Generator:** `python scripts/generate_synthetic_data.py --scale medium` (Requires Python 3.9+, `faker`, `pandas`)
4. **Deploy dbt Models:** `dbt run --target dev` (Ensure `dbt-databricks` is installed and `profiles.yml` is configured)

## Databricks Genie Setup
1. Open Databricks SQL -> Genie Spaces.
2. Create a new Genie Space pointing to the `placewise_semantic` schema.
3. Import instructions from `docs/genie_semantics.md`.
4. Test with sample questions from `docs/question_traceability.md`.

## Known Limitations
- Synthetic data may lack extreme outliers present in real datasets.
- Genie occasionally struggles with highly complex nested aggregations without explicit semantic measures.

## Next Steps When Real Data Arrives
1. Update `scripts/ingest_real_data.py` to map source formats to Bronze schemas.
2. Refine Data Quality rules based on observed real-world anomalies.
3. Validate Genie accuracy against real data questions.
