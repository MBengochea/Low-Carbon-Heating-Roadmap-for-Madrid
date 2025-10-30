SELECT @@secure_file_priv;

(
  SELECT 
    'postal_code','e_surface_m2','e_pct_surface_heated','e_heating_demand_kwh_m2_a',
    'final_heating_kwh_m2_a','nonren_co2_heating_kg_m2_a','e_hotwater_demand_kwh_m2_a',
    'district_id','renta_bruta_media','building_co2_kg'
  UNION ALL
  SELECT 
    postal_code, e_surface_m2, e_pct_surface_heated, e_heating_demand_kwh_m2_a,
    final_heating_kwh_m2_a, nonren_co2_heating_kg_m2_a, e_hotwater_demand_kwh_m2_a,
    district_id, renta_bruta_media, building_co2_kg
  FROM buildings
)
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.4/Uploads/buildings_train.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n';


