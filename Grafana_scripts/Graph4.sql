SELECT
    FLOOR(glucose / 10) * 10 AS glucose_range,  -- Group by ranges of 10
    COUNT(*) AS frequency
FROM
    predictions
GROUP BY
    glucose_range