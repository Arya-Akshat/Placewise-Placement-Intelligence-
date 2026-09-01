MERGE INTO placewise.silver.job_postings target
USING (
    SELECT id, _ingested_at, payload FROM placewise.bronze.job_postings_raw
) source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;\n