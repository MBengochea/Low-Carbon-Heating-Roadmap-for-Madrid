def feature_columns(df):
    return [
        "e_heating_demand_kwh_m2_a",
        "final_heating_kwh_m2_a",
        "nonren_co2_heating_kg_m2_a",
        "renta_bruta_media"
    ]

def build_pipeline(X):
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.impute import SimpleImputer
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])