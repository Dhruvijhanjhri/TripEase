"""
Step 5: Train fare prediction model using easemytrip.csv.

Follows the approved ML pipeline design (Step 4). No Django integration.
Run from project root: python -m ml.train_fare_model

- Loads data/easemytrip.csv
- Preprocesses per design (drop non-predictive, parse dates/times, encode categoricals)
- Time-based train/validation/test split on Departure Date
- Trains Linear Regression (baseline) and Random Forest
- Evaluates with MAE, RMSE, R²; prints comparison and interpretation
- Saves best model and preprocessing to ml_models/
"""

from __future__ import annotations

import os
import re
from datetime import datetime

import pickle

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

# Paths: run from project root (parent of ml/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "ml_models")
DATA_FILE = os.path.join(DATA_DIR, "easemytrip.csv")

# Non-predictive columns to drop (per Step 4: identifiers and scrape-time only)
DROP_COLUMNS = ["Uniq Id", "Crawl Timestamp"]

# Categorical columns to target-encode (Source, Destination, Layovers, primary airline)
CAT_COLUMNS = ["Source", "Destination", "Layover1", "Layover2", "Layover3", "primary_airline"]

# Numerical feature columns used for modeling (after encoding and engineering)
NUMERIC_FEATURE_COLUMNS = [
    "Number Of Stops",
    "total_duration_minutes",
    "departure_day_of_week",
    "departure_month",
    "departure_hour",
    "is_weekend",
] + [f"{c}_encoded" for c in CAT_COLUMNS]

TARGET_COLUMN = "Fare"


def load_data() -> pd.DataFrame:
    """Load easemytrip.csv from data/."""
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Data file not found: {DATA_FILE}")
    df = pd.read_csv(DATA_FILE)
    print(f"Loaded {len(df)} rows from {DATA_FILE}")
    return df


def drop_non_predictive(df: pd.DataFrame) -> pd.DataFrame:
    """Drop identifier and scrape-time columns (no predictive use, leakage risk)."""
    df = df.copy()
    for col in DROP_COLUMNS:
        if col in df.columns:
            df = df.drop(columns=[col])
    print(f"Dropped non-predictive columns: {DROP_COLUMNS}")
    return df


def parse_departure_date(s: str) -> datetime | None:
    """Parse '23Apr2020' -> datetime. Returns None on failure."""
    if pd.isna(s) or not str(s).strip():
        return None
    s = str(s).strip()
    try:
        return datetime.strptime(s, "%d%b%Y")
    except ValueError:
        return None


def parse_time_to_hour(s: str) -> float:
    """Parse '13:10' -> hour (13). Returns 0 on failure."""
    if pd.isna(s) or not str(s).strip():
        return 0.0
    s = str(s).strip()
    parts = s.split(":")
    if len(parts) >= 1 and parts[0].isdigit():
        return float(int(parts[0]))
    return 0.0


def parse_total_time_minutes(s: str) -> float:
    """Parse '08h 50m' or '12h 10m' -> total minutes. Returns 0 on failure."""
    if pd.isna(s) or not str(s).strip():
        return 0.0
    s = str(s).strip()
    # Match "Nh" and optionally "Nm" (e.g. "8h 50m", "08h 50m", "12h 10m")
    h_match = re.search(r"(\d+)\s*h", s, re.IGNORECASE)
    m_match = re.search(r"(\d+)\s*m", s, re.IGNORECASE)
    hours = int(h_match.group(1)) if h_match else 0
    mins = int(m_match.group(1)) if m_match else 0
    return hours * 60.0 + mins


def engineer_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Parse date/time columns and add day, month, hour, duration in minutes, is_weekend."""
    df = df.copy()
    # Departure Date -> datetime
    df["_dep_dt"] = df["Departure Date"].map(parse_departure_date)
    # Drop rows where we could not parse departure date (needed for time-based split)
    before = len(df)
    df = df.dropna(subset=["_dep_dt"])
    if len(df) < before:
        print(f"Dropped {before - len(df)} rows with unparseable Departure Date")

    df["departure_day_of_week"] = df["_dep_dt"].dt.dayofweek
    df["departure_month"] = df["_dep_dt"].dt.month
    df["is_weekend"] = (df["departure_day_of_week"] >= 5).astype(int)

    df["departure_hour"] = df["Departure Time"].astype(str).map(parse_time_to_hour)
    df["total_duration_minutes"] = df["Total Time"].astype(str).map(parse_total_time_minutes)

    df = df.drop(columns=["_dep_dt"])
    print("Engineered temporal features: departure_day_of_week, departure_month, departure_hour, total_duration_minutes, is_weekend")
    return df


def treat_layovers(df: pd.DataFrame) -> pd.DataFrame:
    """Treat empty layovers as 'NoStop' (structural no-stop, not missing at random)."""
    df = df.copy()
    for col in ["Layover1", "Layover2", "Layover3"]:
        if col in df.columns:
            df[col] = df[col].fillna("NoStop").replace("", "NoStop")
    print("Layovers: empty values set to 'NoStop'")
    return df


def derive_primary_airline(df: pd.DataFrame) -> pd.DataFrame:
    """Derive primary_airline = first segment of Flight Operator (before first '|')."""
    df = df.copy()
    if "Flight Operator" not in df.columns:
        df["primary_airline"] = "Unknown"
        return df
    df["primary_airline"] = df["Flight Operator"].astype(str).str.split("|").str[0].str.strip()
    df["primary_airline"] = df["primary_airline"].replace("", "Unknown").fillna("Unknown")
    print("Derived primary_airline from Flight Operator")
    return df


def target_encode_fit_transform(
    df: pd.DataFrame,
    cat_columns: list[str],
    target: str,
    encodings: dict[str, dict[str, float]] | None = None,
    global_mean: float | None = None,
) -> tuple[pd.DataFrame, dict[str, dict[str, float]], float]:
    """
    Target encoding: replace category with mean(target) per category.
    Fit: pass encodings=None, returns (encoded_df, encodings, global_mean).
    Transform: pass encodings and global_mean, returns (encoded_df, encodings, global_mean).
    Unseen categories get global_mean (avoids leakage from val/test).
    """
    if global_mean is None:
        global_mean = float(df[target].mean())
    if encodings is None:
        encodings = {}
    out = df.copy()
    for col in cat_columns:
        if col not in out.columns:
            continue
        if col not in encodings:
            # Fit: compute mean Fare per category on this dataframe
            encodings[col] = df.groupby(col)[target].mean().to_dict()
        # Map; unseen -> global_mean
        out[f"{col}_encoded"] = out[col].map(encodings[col]).fillna(global_mean)
    return out, encodings, global_mean


def build_feature_matrix(
    df: pd.DataFrame,
    numeric_feature_columns: list[str],
    target: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Build X and y from dataframe; drop rows with any missing in feature or target."""
    available = [c for c in numeric_feature_columns if c in df.columns]
    use_df = df[available + [target]].dropna()
    X = use_df[available].values
    y = use_df[target].values
    return X, y


def time_based_split(
    df: pd.DataFrame,
    date_col: str = "Departure Date",
    train_frac: float = 0.70,
    val_frac: float = 0.15,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split by time: sort by date, then train / validation / test.
    Uses parsed datetime stored in _dep_dt if present; else parses date_col.
    """
    df = df.copy()
    if "_dep_dt" not in df.columns:
        df["_dep_dt"] = df[date_col].map(parse_departure_date)
        df = df.dropna(subset=["_dep_dt"])
    df = df.sort_values("_dep_dt").reset_index(drop=True)
    n = len(df)
    t1 = int(n * train_frac)
    t2 = int(n * (train_frac + val_frac))
    train_df = df.iloc[:t1]
    val_df = df.iloc[t1:t2]
    test_df = df.iloc[t2:]
    if "_dep_dt" in train_df.columns:
        train_df = train_df.drop(columns=["_dep_dt"])
        val_df = val_df.drop(columns=["_dep_dt"])
        test_df = test_df.drop(columns=["_dep_dt"])
    print(f"Time-based split: train={len(train_df)}, val={len(val_df)}, test={len(test_df)}")
    return train_df, val_df, test_df


def main() -> None:
    print("=" * 60)
    print("Step 5: Fare model training (easemytrip.csv)")
    print("=" * 60)

    # 1. Load
    df = load_data()
    df = drop_non_predictive(df)
    df = engineer_temporal_features(df)
    df = treat_layovers(df)
    df = derive_primary_airline(df)

    # Cast target and Number Of Stops
    df[TARGET_COLUMN] = pd.to_numeric(df[TARGET_COLUMN], errors="coerce")
    df["Number Of Stops"] = pd.to_numeric(df["Number Of Stops"], errors="coerce")
    df = df.dropna(subset=[TARGET_COLUMN, "Number Of Stops"])

    # 2. Target encoding (fit on full dataset for simplicity; in production fit on train only)
    # We will re-fit encoding on train only and apply to val/test below.
    train_df, val_df, test_df = time_based_split(df, train_frac=0.70, val_frac=0.15)

    # Fit target encoding on TRAIN only (avoid leakage)
    train_df, encodings, global_mean = target_encode_fit_transform(
        train_df, CAT_COLUMNS, TARGET_COLUMN
    )
    val_df, encodings, _ = target_encode_fit_transform(
        val_df, CAT_COLUMNS, TARGET_COLUMN, encodings=encodings, global_mean=global_mean
    )
    test_df, encodings, _ = target_encode_fit_transform(
        test_df, CAT_COLUMNS, TARGET_COLUMN, encodings=encodings, global_mean=global_mean
    )
    print("Categorical encoding: target encoding (mean Fare per category) fitted on train only; unseen categories use global mean. Reason: single encoding for both linear and tree models, avoids high-dimensional one-hot for many cities/airlines.")

    # 3. Build feature matrices
    feats = [c for c in NUMERIC_FEATURE_COLUMNS if c in train_df.columns]
    X_train, y_train = build_feature_matrix(train_df, feats, TARGET_COLUMN)
    X_val, y_val = build_feature_matrix(val_df, feats, TARGET_COLUMN)
    X_test, y_test = build_feature_matrix(test_df, feats, TARGET_COLUMN)
    print(f"Feature matrix shape: train {X_train.shape}, val {X_val.shape}, test {X_test.shape}")

    # 4. Scale for Linear Regression only (tree model uses unscaled)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    # 5. Train two models
    print("\nTraining models...")
    lr = LinearRegression()
    lr.fit(X_train_scaled, y_train)

    rf = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42)
    rf.fit(X_train, y_train)

    # 6. Evaluate: MAE, RMSE, R² on validation and test
    def eval_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
        return {
            "MAE": float(mean_absolute_error(y_true, y_pred)),
            "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "R2": float(r2_score(y_true, y_pred)),
        }

    lr_val = eval_metrics(y_val, lr.predict(X_val_scaled))
    lr_test = eval_metrics(y_test, lr.predict(X_test_scaled))
    rf_val = eval_metrics(y_val, rf.predict(X_val))
    rf_test = eval_metrics(y_test, rf.predict(X_test))

    # 7. Model comparison table
    print("\n" + "=" * 60)
    print("Model comparison (Validation / Test)")
    print("=" * 60)
    print(f"{'Model':<25} {'MAE (val)':<12} {'MAE (test)':<12} {'RMSE (val)':<12} {'RMSE (test)':<12} {'R² (val)':<10} {'R² (test)':<10}")
    print("-" * 95)
    print(f"{'Linear Regression':<25} {lr_val['MAE']:<12.2f} {lr_test['MAE']:<12.2f} {lr_val['RMSE']:<12.2f} {lr_test['RMSE']:<12.2f} {lr_val['R2']:<10.4f} {lr_test['R2']:<10.4f}")
    print(f"{'Random Forest':<25} {rf_val['MAE']:<12.2f} {rf_test['MAE']:<12.2f} {rf_val['RMSE']:<12.2f} {rf_test['RMSE']:<12.2f} {rf_val['R2']:<10.4f} {rf_test['R2']:<10.4f}")
    print("=" * 95)

    # 8. Short interpretation (plain English)
    print("\nInterpretation:")
    print("- MAE: average absolute error in fare units (e.g. currency). Lower is better.")
    print("- RMSE: penalizes large errors more; useful for cost-sensitive decisions.")
    print("- R²: share of fare variance explained by the model (0–1); higher is better.")
    best_val_mae = min(lr_val["MAE"], rf_val["MAE"])
    if rf_val["MAE"] <= lr_val["MAE"]:
        print("- Random Forest achieves better (or equal) validation MAE than Linear Regression, which is typical for non-linear fare patterns.")
    else:
        print("- Linear Regression achieves better validation MAE here; Random Forest may benefit from more data or different hyperparameters later.")
    print("- Test metrics show how well the model generalizes to unseen time periods; use them for final reporting.")

    # 9. Save best model (by validation MAE) and preprocessing to ml_models/
    os.makedirs(MODELS_DIR, exist_ok=True)
    if rf_val["MAE"] <= lr_val["MAE"]:
        best_model = rf
        best_name = "Random Forest"
        use_scaler = False
    else:
        best_model = lr
        best_name = "Linear Regression"
        use_scaler = True

    model_path = os.path.join(MODELS_DIR, "fare_model_final.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(best_model, f)
    print(f"\nSaved best model ({best_name}) to {model_path}")

    prep = {
        "scaler": scaler if use_scaler else None,
        "target_encodings": encodings,
        "global_mean": global_mean,
        "feature_columns": feats,
        "target_column": TARGET_COLUMN,
        "model_type": best_name,
        "scale_features": use_scaler,
    }
    prep_path = os.path.join(MODELS_DIR, "fare_preprocessing.pkl")
    with open(prep_path, "wb") as f:
        pickle.dump(prep, f)
    print(f"Saved preprocessing (scaler, encodings, feature list) to {prep_path}.")
    print("Done.")


if __name__ == "__main__":
    main()
