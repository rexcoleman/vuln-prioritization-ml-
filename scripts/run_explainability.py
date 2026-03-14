#!/usr/bin/env python3
"""Run SHAP explainability analysis on the best model.

Produces:
  - Global SHAP summary plot (which features matter most across all CVEs)
  - SHAP bar plot (top 20 features)
  - Feature importance comparison: SHAP vs model-native vs practitioner keywords
  - Local explanations for interesting CVEs (high SHAP, disagreement with CVSS)

Usage:
    python scripts/run_explainability.py --seed 42
    python scripts/run_explainability.py --seed 42 --sample-frac 0.01  # smoke test
"""
import argparse
import json
import pickle
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

OUTPUT_DIR = Path("outputs/explainability")
FIGURES_DIR = Path("outputs/figures")
DATA_DIR = Path("data/processed")
MODEL_DIR = Path("outputs/models")


def load_model_and_data(seed, sample_frac=1.0):
    """Load best model and test data."""
    model_file = MODEL_DIR / f"best_model_seed{seed}.pkl"
    with open(model_file, "rb") as f:
        bundle = pickle.load(f)

    model = bundle["model"]
    model_name = bundle["name"]
    feature_cols = bundle["feature_cols"]

    test = pd.read_parquet(DATA_DIR / "test.parquet")
    if sample_frac < 1.0:
        test = test.sample(frac=sample_frac, random_state=seed)

    X_test = test[feature_cols].fillna(0)
    y_test = test["exploited"].values

    return model, model_name, X_test, y_test, feature_cols, test


def run_shap_analysis(model, model_name, X_test, feature_cols, max_samples=1000):
    """Compute SHAP values."""
    print(f"Computing SHAP values for {model_name}...")

    # Subsample for SHAP (can be slow on large datasets)
    if len(X_test) > max_samples:
        X_shap = X_test.sample(n=max_samples, random_state=42)
        print(f"  Subsampled to {max_samples} for SHAP computation")
    else:
        X_shap = X_test

    # Choose appropriate SHAP explainer
    if model_name in ["random_forest", "xgboost"]:
        explainer = shap.TreeExplainer(model)
    else:
        explainer = shap.LinearExplainer(model, X_shap)

    shap_values = explainer.shap_values(X_shap)

    # For binary classification, take class 1 values
    if isinstance(shap_values, list) and len(shap_values) == 2:
        shap_values = shap_values[1]

    print(f"  SHAP values shape: {shap_values.shape}")
    return shap_values, X_shap


def plot_shap_summary(shap_values, X_shap, feature_cols, seed):
    """Generate SHAP summary plot (beeswarm)."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 10))
    shap.summary_plot(shap_values, X_shap, feature_names=feature_cols,
                      max_display=25, show=False)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / f"shap_summary_seed{seed}.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {FIGURES_DIR / f'shap_summary_seed{seed}.png'}")


def plot_shap_bar(shap_values, feature_cols, seed):
    """Generate SHAP bar plot (mean absolute SHAP)."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    importance_df = pd.DataFrame({
        "feature": feature_cols,
        "mean_abs_shap": mean_abs_shap,
    }).sort_values("mean_abs_shap", ascending=False)

    # Top 20
    top20 = importance_df.head(20)

    plt.figure(figsize=(10, 8))
    plt.barh(range(len(top20)), top20["mean_abs_shap"].values[::-1])
    plt.yticks(range(len(top20)), top20["feature"].values[::-1])
    plt.xlabel("Mean |SHAP value|")
    plt.title("Top 20 Features by SHAP Importance")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / f"shap_bar_top20_seed{seed}.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {FIGURES_DIR / f'shap_bar_top20_seed{seed}.png'}")

    return importance_df


def analyze_practitioner_features(importance_df, seed):
    """Compare practitioner keyword features vs other features."""
    kw_features = importance_df[importance_df["feature"].str.startswith("kw_")]
    non_kw = importance_df[~importance_df["feature"].str.startswith("kw_")]

    print(f"\n=== Practitioner Keyword Feature Analysis ===")
    print(f"Keyword features in top 20: {len(kw_features[kw_features.index < 20])}")
    print(f"\nKeyword feature rankings:")
    for _, row in kw_features.iterrows():
        rank = importance_df.index.get_loc(row.name) + 1
        print(f"  #{rank}: {row['feature']} (SHAP={row['mean_abs_shap']:.4f})")

    # Save analysis
    analysis = {
        "keyword_features": kw_features.to_dict("records"),
        "top_20_features": importance_df.head(20).to_dict("records"),
        "keyword_in_top_20": int(len(kw_features[kw_features.index < 20])),
        "keyword_mean_importance": float(kw_features["mean_abs_shap"].mean()) if len(kw_features) > 0 else 0,
        "non_keyword_mean_importance": float(non_kw.head(20)["mean_abs_shap"].mean()),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_DIR / f"practitioner_analysis_seed{seed}.json", "w") as f:
        json.dump(analysis, f, indent=2)

    return analysis


def main():
    parser = argparse.ArgumentParser(description="Run SHAP explainability")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--sample-frac", type=float, default=1.0)
    parser.add_argument("--max-shap-samples", type=int, default=1000)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading model and data...")
    model, model_name, X_test, y_test, feature_cols, test_df = load_model_and_data(
        args.seed, args.sample_frac
    )
    print(f"Model: {model_name} | Test: {len(X_test):,} | Features: {len(feature_cols)}")

    # SHAP analysis
    shap_values, X_shap = run_shap_analysis(
        model, model_name, X_test, feature_cols, max_samples=args.max_shap_samples
    )

    # Plots
    print("\nGenerating plots...")
    plot_shap_summary(shap_values, X_shap, feature_cols, args.seed)
    importance_df = plot_shap_bar(shap_values, feature_cols, args.seed)

    # Practitioner feature analysis
    practitioner_analysis = analyze_practitioner_features(importance_df, args.seed)

    # Save full importance ranking
    importance_df.to_csv(OUTPUT_DIR / f"feature_importance_seed{args.seed}.csv", index=False)

    print(f"\n=== Explainability complete for seed {args.seed} ===")


if __name__ == "__main__":
    main()
