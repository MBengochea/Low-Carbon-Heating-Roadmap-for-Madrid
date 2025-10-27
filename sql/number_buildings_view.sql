USE madrid_roadmap;

CREATE OR REPLACE VIEW district_building_count AS
SELECT 
    district_id,
    COUNT(*) AS num_buildings
FROM buildings
WHERE district_id IS NOT NULL
GROUP BY district_id;

SELECT * FROM district_building_count ORDER BY num_buildings DESC;
