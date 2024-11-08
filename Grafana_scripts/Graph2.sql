SELECT
    created_date AS date,
    AVG(glucose) AS avg_glucose,
    AVG(bmi) AS avg_bmi
FROM
    predictions
WHERE
    created_date >= NOW() - INTERVAL '14 days'
GROUP BY
    created_date
ORDER BY
    created_date;