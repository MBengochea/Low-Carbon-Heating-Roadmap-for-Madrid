USE madrid_roadmap;


CREATE OR REPLACE VIEW district_priority AS
WITH ordered AS (
    SELECT 
        district_id,
        total_co2_kg,
        intensity_kg_m2,
        avg_income,
        SUM(total_co2_kg) OVER (ORDER BY total_co2_kg DESC) AS cum_emissions,
        SUM(total_co2_kg) OVER () AS grand_total
    FROM district_emissions
),
with_flag AS (
    SELECT 
        district_id,
        total_co2_kg,
        intensity_kg_m2,
        avg_income,
        cum_emissions,
        cum_emissions / NULLIF(grand_total,0) AS cum_share,
        CASE WHEN cum_emissions / NULLIF(grand_total,0) <= 0.8 
             THEN 'Pareto Top 20%' ELSE 'Other' END AS pareto_flag
    FROM ordered
),
median_income AS (
    SELECT AVG(renta_bruta_media) AS median_income
    FROM (
        SELECT renta_bruta_media,
               ROW_NUMBER() OVER (ORDER BY renta_bruta_media) AS rn,
               COUNT(*) OVER () AS cnt
        FROM buildings
    ) t
    WHERE rn IN (FLOOR((cnt + 1) / 2), CEIL((cnt + 1) / 2))
)
SELECT wf.*, m.median_income
FROM with_flag wf
CROSS JOIN median_income m
WHERE pareto_flag = 'Pareto Top 20%'
  AND avg_income < m.median_income;
  
SELECT * FROM district_priority LIMIT 10;postal_to_district



