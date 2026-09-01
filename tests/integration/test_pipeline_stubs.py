def test_bronze_to_silver_students():
    """Tests that bronze->silver student transformation:
    - Maps placement_status correctly
    - Validates CGPA range
    - Deduplicates on student_id
    - Preserves record count (minus quarantined)
    """
    pass  # TODO: implement with Databricks test cluster

def test_silver_to_gold_student_placement_profile():
    """Tests that gold profile:
    - Contains all score components
    - placement_readiness_score = weighted sum of components
    - No null student_id
    - Funnel counts consistent
    """
    pass  # TODO: implement with Databricks test cluster
