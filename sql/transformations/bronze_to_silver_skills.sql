MERGE INTO placewise.silver.skills target
USING (
    SELECT id, _ingested_at, payload FROM placewise.bronze.skills_raw
) source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;\n