CREATE DATABASE madrid_roadmap;
USE madrid_roadmap;

CREATE TABLE buildings (
    postal_code VARCHAR(10),
    e_surface_m2 DOUBLE,
    e_pct_surface_heated DOUBLE,
    e_heating_demand_kwh_m2_a DOUBLE,
    final_heating_kwh_m2_a DOUBLE,
    nonren_heating_kwh_m2_a DOUBLE,
    nonren_co2_heating_kg_m2_a DOUBLE,
    e_hotwater_demand_kwh_m2_a DOUBLE,
    district_id VARCHAR(20)   -- will be filled after join
);

SET SQL_SAFE_UPDATES = 0;

SELECT DISTINCT b.postal_code AS b_code, p.postal_code AS p_code
FROM buildings b
LEFT JOIN postal_to_district p ON b.postal_code = p.postal_code
WHERE p.postal_code IS NULL
LIMIT 10;

UPDATE buildings b
JOIN postal_to_district p
  ON TRIM(CAST(b.postal_code AS CHAR)) = TRIM(CAST(p.postal_code AS CHAR))
SET b.district_id = p.district_id
WHERE b.district_id IS NULL;

ALTER TABLE buildings
ADD COLUMN renta_bruta_media DOUBLE;

# Compute absolute emissions per building 

ALTER TABLE buildings
ADD COLUMN building_co2_kg DOUBLE;
### For work in case of nulls
UPDATE buildings
SET building_co2_kg = COALESCE(nonren_co2_heating_kg_m2_a,0) * COALESCE(e_surface_m2,0);
 
# Agregate by district

CREATE OR REPLACE VIEW district_emissions AS
SELECT 
    district_id,
    SUM(building_co2_kg) AS total_co2_kg,
    SUM(COALESCE(e_surface_m2,0)) AS total_surface_m2,
    SUM(building_co2_kg) / NULLIF(SUM(COALESCE(e_surface_m2,0)),0) AS intensity_kg_m2,
    AVG(renta_bruta_media) AS avg_income
FROM buildings
WHERE district_id IS NOT NULL
GROUP BY district_id;


# Pareto Analysis

WITH ordered AS (
    SELECT 
        district_id,
        total_co2_kg,
        intensity_kg_m2,
        avg_income,
        SUM(total_co2_kg) OVER (ORDER BY total_co2_kg DESC) AS cum_emissions,
        SUM(total_co2_kg) OVER () AS grand_total
    FROM district_emissions
)
SELECT 
    district_id,
    total_co2_kg,
    intensity_kg_m2,
    avg_income,
    cum_emissions,
    cum_emissions / grand_total AS cum_share,
    CASE WHEN cum_emissions / grand_total <= 0.8 THEN 'Pareto Top 20%' ELSE 'Other' END AS pareto_flag
FROM ordered
ORDER BY total_co2_kg DESC;

# Priority zones 

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
SELECT wf.*
FROM with_flag wf
CROSS JOIN median_income m
WHERE pareto_flag = 'Pareto Top 20%'
  AND avg_income < m.median_income
ORDER BY intensity_kg_m2 DESC;







