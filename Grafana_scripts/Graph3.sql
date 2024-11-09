WITH risk_conditions AS (
    SELECT
        NOW()::date + (row_number() OVER ())::int AS created_date,

        COUNT(CASE WHEN glucose > 150 AND bmi > 30 THEN 1 END) AS high_glucose_high_bmi,
        COUNT(CASE WHEN hypertension = 1 THEN 1 END) AS hypertension_count,
        COUNT(CASE WHEN age >= 60 THEN 1 END) AS age_risk_group

    FROM
        predictions
    WHERE
        glucose IS NOT NULL AND bmi IS NOT NULL AND age IS NOT NULL
    GROUP BY
        created_date
    ORDER BY
        created_date
)

-- Main query to fetch data for Grafana
SELECT
    created_date,
    high_glucose_high_bmi,
    hypertension_count,
    age_risk_group
FROM
    risk_conditions
ORDER BY
    created_date;

