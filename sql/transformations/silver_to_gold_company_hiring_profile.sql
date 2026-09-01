CREATE OR REPLACE TABLE placewise.gold.company_hiring_profile AS
WITH job_postings_agg AS (
    SELECT company_id,
           COUNT(DISTINCT job_posting_id) AS job_postings_count,
           SUM(openings) AS openings_count
    FROM placewise.silver.job_postings
    GROUP BY company_id
),
applications_agg AS (
    SELECT jp.company_id,
           COUNT(DISTINCT a.application_id) AS applications_count,
           COUNT(DISTINCT CASE WHEN ash.status IN ('SHORTLISTED','INTERVIEW','OFFERED','ACCEPTED') THEN a.application_id END) AS shortlisted_count,
           COUNT(DISTINCT CASE WHEN ash.status IN ('INTERVIEW','OFFERED','ACCEPTED') THEN a.application_id END) AS interviews_count
    FROM placewise.silver.applications a
    JOIN placewise.silver.job_postings jp ON a.job_posting_id = jp.job_posting_id
    LEFT JOIN placewise.silver.application_status_history ash ON a.application_id = ash.application_id
    GROUP BY jp.company_id
),
interviews_agg AS (
    SELECT jp.company_id,
           AVG(iv.overall_score) AS average_interview_score
    FROM placewise.silver.interviews iv
    JOIN placewise.silver.applications a ON iv.application_id = a.application_id
    JOIN placewise.silver.job_postings jp ON a.job_posting_id = jp.job_posting_id
    GROUP BY jp.company_id
),
offers_agg AS (
    SELECT jp.company_id,
           COUNT(DISTINCT o.offer_id) AS offers_count,
           COUNT(DISTINCT CASE WHEN o.offer_status = 'ACCEPTED' THEN o.offer_id END) AS accepted_offers_count
    FROM placewise.silver.offers o
    JOIN placewise.silver.applications a ON o.application_id = a.application_id
    JOIN placewise.silver.job_postings jp ON a.job_posting_id = jp.job_posting_id
    GROUP BY jp.company_id
),
placements_agg AS (
    SELECT jp.company_id,
           COUNT(DISTINCT p.placement_id) AS placements_count,
           ROUND(AVG(p.ctc_lpa), 2) AS average_ctc_lpa,
           ROUND(MEDIAN(p.ctc_lpa), 2) AS median_ctc_lpa,
           ROUND(MAX(p.ctc_lpa), 2) AS highest_ctc_lpa,
           ROUND(MIN(p.ctc_lpa), 2) AS lowest_ctc_lpa
    FROM placewise.silver.placements p
    JOIN placewise.silver.offers o ON p.offer_id = o.offer_id
    JOIN placewise.silver.applications a ON o.application_id = a.application_id
    JOIN placewise.silver.job_postings jp ON a.job_posting_id = jp.job_posting_id
    GROUP BY jp.company_id
)
SELECT
    c.company_id,
    c.company_name,
    c.industry,
    c.company_type,
    CASE WHEN c.is_product_company THEN 'PRODUCT' WHEN c.is_service_company THEN 'SERVICES' ELSE 'OTHER' END AS product_or_service,
    COALESCE(jpa.job_postings_count, 0) AS job_postings_count,
    COALESCE(jpa.openings_count, 0) AS openings_count,
    COALESCE(aa.applications_count, 0) AS applications_count,
    COALESCE(aa.shortlisted_count, 0) AS shortlisted_count,
    COALESCE(aa.interviews_count, 0) AS interviews_count,
    COALESCE(oa.offers_count, 0) AS offers_count,
    COALESCE(oa.accepted_offers_count, 0) AS accepted_offers_count,
    COALESCE(pa.placements_count, 0) AS placements_count,
    pa.average_ctc_lpa,
    pa.median_ctc_lpa,
    pa.highest_ctc_lpa,
    pa.lowest_ctc_lpa,
    CASE WHEN COALESCE(aa.applications_count, 0) > 0 THEN ROUND(COALESCE(aa.interviews_count, 0) * 100.0 / aa.applications_count, 2) END AS application_to_interview_rate,
    CASE WHEN COALESCE(aa.interviews_count, 0) > 0 THEN ROUND(COALESCE(oa.offers_count, 0) * 100.0 / aa.interviews_count, 2) END AS interview_to_offer_rate,
    CASE WHEN COALESCE(oa.offers_count, 0) > 0 THEN ROUND(COALESCE(oa.accepted_offers_count, 0) * 100.0 / oa.offers_count, 2) END AS offer_acceptance_rate,
    CASE WHEN COALESCE(aa.applications_count, 0) > 0 THEN ROUND(COALESCE(pa.placements_count, 0) * 100.0 / aa.applications_count, 2) END AS application_to_placement_rate,
    ROUND(ia.average_interview_score, 2) AS average_interview_score
FROM placewise.silver.companies c
LEFT JOIN job_postings_agg jpa ON c.company_id = jpa.company_id
LEFT JOIN applications_agg aa ON c.company_id = aa.company_id
LEFT JOIN interviews_agg ia ON c.company_id = ia.company_id
LEFT JOIN offers_agg oa ON c.company_id = oa.company_id
LEFT JOIN placements_agg pa ON c.company_id = pa.company_id;
