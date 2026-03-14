#!/usr/bin/env python3
"""Train ML models for vulnerability exploitability prediction.

Models: Random Forest, XGBoost, Logistic Regression.
All models must beat the best baseline (CVSS/EPSS threshold) to be interesting.

Usage:
    python scripts/train_models.py --seed 42
    python scripts/train_models.py --seed 42 --sample-frac 0.01  # smoke test
"""
import argparse
import json
import pickle
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    roc_auc_score, average_precision_score, classification_report,
)
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

OUTPUT_DIR = Path("outputs/models")
DATA_DIR = Path("data/processed")


def load_data(sample_frac=1.0, seed=42):
    """Load train/test data and feature columns."""
    train = pd.read_parquet(DATA_DIR / "train.parquet")
    test = pd.read_parquet(DATA_DIR / "test.parquet")

    with open(DATA_DIR / "feature_cols.json") as f:
        feature_cols = json.load(f)

    if sample_frac < 1.0:
        train = train.sample(frac=sample_frac, random_state=seed)
        test = test.sample(frac=sample_frac, random_state=seed)

    # Prepare X, y
    X_train = train[feature_cols].fillna(0).values
    y_train = train["exploited"].values
    X_test = test[feature_cols].fillna(0).values
    y_test = test["exploited"].values

    return X_train, y_train, X_test, y_test, feature_cols, train, test


def evaluate(y_true, y_pred, y_prob):
    """Compute classification metrics."""
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }
    try:
        metrics["auc_roc"] = float(roc_auc_score(y_true, y_prob))
        metrics["auc_pr"] = float(average_precision_score(y_true, y_prob))
    except ValueError:
        metrics["auc_roc"] = None
        metrics["auc_pr"] = None
    return metrics


def train_random_forest(X_train, y_train, X_test, y_test, seed):
    """Train Random Forest."""
    print("Training Random Forest...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=seed,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    metrics = evaluate(y_test, y_pred, y_prob)
    print(f"  AUC={metrics.get('auc_roc', 'N/A'):.4f}, F1={metrics['f1']:.4f}")
    return model, metrics


def train_xgboost(X_train, y_train, X_test, y_test, seed):
    """Train XGBoost."""
    print("Training XGBoost...")
    # Handle class imbalance
    pos_count = y_train.sum()
    neg_count = len(y_train) - pos_count
    scale_pos_weight = neg_count / max(pos_count, 1)

    model = XGBClassifier(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
        random_state=seed,
        n_jobs=-1,
        verbosity=0,
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    metrics = evaluate(y_test, y_pred, y_prob)
    print(f"  AUC={metrics.get('auc_roc', 'N/A'):.4f}, F1={metrics['f1']:.4f}")
    return model, metrics


def train_logistic_regression(X_train, y_train, X_test, y_test, seed):
    """Train Logistic Regression (with scaling)."""
    print("Training Logistic Regression...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=seed,
        solver="lbfgs",
    )
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    metrics = evaluate(y_test, y_pred, y_prob)
    print(f"  AUC={metrics.get('auc_roc', 'N/A'):.4f}, F1={metrics['f1']:.4f}")
    return model, metrics, scaler


def main():
    parser = argparse.ArgumentParser(description="Train ML models")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--sample-frac", type=float, default=1.0)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading data...")
    X_train, y_train, X_test, y_test, feature_cols, train_df, test_df = load_data(
        sample_frac=args.sample_frac, seed=args.seed
    )
    print(f"Train: {X_train.shape} | Test: {X_test.shape}")
    print(f"Features: {len(feature_cols)}")
    print(f"Train exploit rate: {y_train.mean()*100:.1f}%")
    print(f"Test exploit rate: {y_test.mean()*100:.1f}%\n")

    results = {}

    # Train all models
    rf_model, rf_metrics = train_random_forest(X_train, y_train, X_test, y_test, args.seed)
    results["random_forest"] = rf_metrics

    xgb_model, xgb_metrics = train_xgboost(X_train, y_train, X_test, y_test, args.seed)
    results["xgboost"] = xgb_metrics

    lr_model, lr_metrics, lr_scaler = train_logistic_regression(
        X_train, y_train, X_test, y_test, args.seed
    )
    results["logistic_regression"] = lr_metrics

    # Find best model
    best_name = max(results, key=lambda k: results[k].get("auc_roc") or 0)
    print(f"\n=== Best Model: {best_name} (AUC={results[best_name].get('auc_roc', 'N/A'):.4f}) ===")

    # Compare against baselines
    baseline_file = Path("outputs/baselines") / f"baselines_seed{args.seed}.json"
    if baseline_file.exists():
        with open(baseline_file) as f:
            baseline_data = json.load(f)
        best_baseline_auc = baseline_data["best_baseline"].get("auc_roc", 0) or 0
        best_model_auc = results[best_name].get("auc_roc", 0) or 0
        improvement = best_model_auc - best_baseline_auc
        print(f"  vs best baseline: {improvement:+.4f} AUC ({improvement/max(best_baseline_auc,0.001)*100:+.1f}%)")

    # Save results
    summary = {
        "seed": args.seed,
        "sample_frac": args.sample_frac,
        "date": datetime.now().isoformat(),
        "train_size": int(X_train.shape[0]),
        "test_size": int(X_test.shape[0]),
        "num_features": len(feature_cols),
        "models": results,
        "best_model": best_name,
        "feature_cols": feature_cols,
    }

    out_file = OUTPUT_DIR / f"models_seed{args.seed}.json"
    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)

    # Save best model for SHAP analysis
    best_model = {"random_forest": rf_model, "xgboost": xgb_model, "logistic_regression": lr_model}[best_name]
    model_file = OUTPUT_DIR / f"best_model_seed{args.seed}.pkl"
    with open(model_file, "wb") as f:
        pickle.dump({"model": best_model, "name": best_name, "feature_cols": feature_cols}, f)

    print(f"\nSaved: {out_file}")
    print(f"Saved: {model_file}")

    # Print full classification report for best model
    print(f"\n=== {best_name} Classification Report ===")
    y_pred = best_model.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=["not_exploited", "exploited"]))


if __name__ == "__main__":
    main()
