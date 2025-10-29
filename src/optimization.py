# src/optimization.py
"""
Optimization helpers.
Provides a priority-first greedy selector as a reliable baseline.
Keep function pure: inputs are dataframes and params, output is a dataframe of selected rows.
"""

from typing import List, Dict, Any
import pandas as pd

def run_priority_greedy(
    df: pd.DataFrame,
    budget: float,
    priority_list: List[int],
    capex_subsidy_pct: float = 0.0,
    opex_factor: float = 1.0,
    co2_factor: float = 1.0,
    adoption_rate_default: float = 0.3
) -> pd.DataFrame:
    """
    Greedy selection that:
    - Applies scenario levers to df (expects columns: district_id, expected_capex_eur, OPEX, expected_saving_kg)
    - Ensures adoption_rate exists (fills with adoption_rate_default)
    - Always attempts to include districts in priority_list first (in given order), then others by ascending district_id
    - Returns dataframe of selected rows with computed total_cost and weighted_saving

    Notes:
    - This is a heuristic designed for clear, auditable rollouts.
    - df is not modified in place; a copy is returned.
    """
    d = df.copy()

    # Ensure adoption_rate column exists
    if "adoption_rate" not in d.columns:
        d["adoption_rate"] = adoption_rate_default
    else:
        d["adoption_rate"] = d["adoption_rate"].fillna(adoption_rate_default)

    # Apply levers
    d["OPEX"] = d.get("OPEX", 0) * opex_factor
    d["expected_capex_eur_subsidized"] = d["expected_capex_eur"] * (1 - capex_subsidy_pct/100.0)
    d["total_cost"] = d["expected_capex_eur_subsidized"] + d["OPEX"]
    d["weighted_saving"] = d["expected_saving_kg"] * d["adoption_rate"] * co2_factor

    selected_rows = []
    budget_left = float(budget)

    # Priority first
    for did in priority_list:
        rows = d[d["district_id"] == did]
        if rows.empty:
            continue
        row = rows.iloc[0]
        if row["total_cost"] <= budget_left:
            selected_rows.append(row)
            budget_left -= row["total_cost"]

    # Then others by ascending district_id
    remaining_ids = [i for i in sorted(d["district_id"].unique()) if i not in priority_list]
    for did in remaining_ids:
        rows = d[d["district_id"] == did]
        if rows.empty:
            continue
        row = rows.iloc[0]
        if row["total_cost"] <= budget_left:
            selected_rows.append(row)
            budget_left -= row["total_cost"]

    if selected_rows:
        result = pd.DataFrame(selected_rows).reset_index(drop=True)
    else:
        result = pd.DataFrame(columns=d.columns)

    return result
