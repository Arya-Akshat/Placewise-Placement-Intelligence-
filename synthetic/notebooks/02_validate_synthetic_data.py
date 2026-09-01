# Databricks notebook for validation
# COMMAND ----------
from validators.synthetic_validator import SyntheticValidator
val = SyntheticValidator()
val.validate('data/synthetic')
