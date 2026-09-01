MERGE INTO placewise.silver.offers target
USING (
    SELECT id, _ingested_at, payload FROM placewise.bronze.offers_raw
) source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;\n