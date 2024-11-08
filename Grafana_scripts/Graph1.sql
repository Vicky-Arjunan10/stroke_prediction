WITH data_with_timestamp AS (
    SELECT
        gender,
        age,
        hypertension,
        heart_diseases,
        glucose,
        bmi,
        DATE_TRUNC('day', NOW() - INTERVAL '1 day' * (ROW_NUMBER() OVER())) AS timestamp
    FROM
        predictions
)
SELECT
    'Heart Disease Breakdown' AS "Category",  -- Label for the type of count
    SUM(CASE WHEN heart_diseases = 1 THEN 1 ELSE 0 END) AS "Heart Disease Count (Red ❌)",  -- Count where heart_diseases = 1
    SUM(CASE WHEN heart_diseases = 0 THEN 1 ELSE 0 END) AS "No Heart Disease Count (Green ✅)",  -- Count where heart_diseases = 0
    COUNT(*) AS "Total Count"  -- Total number of records
FROM
    data_with_timestamp;
