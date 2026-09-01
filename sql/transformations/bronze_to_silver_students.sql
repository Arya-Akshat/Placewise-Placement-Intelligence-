MERGE INTO placewise.silver.students target
USING (
    SELECT id, _ingested_at, payload FROM placewise.bronze.students_raw
) source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;\n