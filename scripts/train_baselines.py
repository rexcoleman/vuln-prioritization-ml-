#!/usr/bin/env python3
"""Train baseline models for vulnerability exploitability prediction.

Baselines:
  - CVSS threshold (predict exploited if CVSS >= threshold)
  - EPSS threshold (predict exploited if EPSS >= threshold)
  - Random (predict majority class)

These establish the floor our ML models must beat.

Usage:
    python scripts/train_baselines.py --seed 42
    python scripts/train_baselines.py --seed 42 --sample-frac 0.01  # smoke test
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    roc_auc_score, average_precision_score, classification_report,
)

OUTPUT_DIR = Path("outputs/baselines")
DATA_DIR = Path("data/processed")


def load_data(sample_frac=1.0, seed=42):
    """Load train/test data."""
    train = pd.read_parquet(DATA_DIR / "train.parquet")
    test = pd.read_parquet(DATA_DIR / "test.parquet")

    if sample_frac < 1.0:
        train = train.sample(frac=sample_frac, random_state=seed)
        test = test.sample(frac=sample_frac, random_state=seed)
        print(f"Sampled: train={len(train):,}, test={len(test):,}")

    return train, test


def evaluate(y_true, y_pred, y_prob=None):
    """Compute standard classification metrics."""
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }
    if y_prob is not None:
        try:
            metrics["auc_roc"] = float(roc_auc_score(y_true, y_prob))
            metrics["auc_pr"] = float(average_precision_score(y_true, y_prob))
        except ValueError:
            metrics["auc_roc"] = None
            metrics["auc_pr"] = None
    return metrics


def cvss_threshold_baseline(test_df, thresholds=None):
    """CVSS threshold baseline: predict exploited if CVSS >= threshold."""
    if thresholds is None:
        thresholds = [4.0, 5.0, 6.0, 7.0, 7.5, 8.0, 9.0]

    y_true = test_df["exploited"].values
    cvss = test_df["cvss_score"].values

    results = []
    for t in thresholds:
        y_pred = (cvss >= t).astype(int)
        metrics = evaluate(y_true, y_pred, y_prob=cvss / 10.0)
        metrics["threshold"] = t
        metrics["method"] = f"cvss_threshold_{t}"
        results.append(metrics)
        print(f"  CVSS >= {t}: F1={metrics['f1']:.3f}, AUC={metrics.get('auc_roc', 'N/A')}")

    return results


def epss_threshold_baseline(test_df, thresholds=None):
    """EPSS threshold baseline: predict exploited if EPSS >= threshold."""
    if thresholds is None:
        thresholds = [0.01, 0.05, 0.1, 0.2, 0.5]

    y_true = test_df["exploited"].values
    epss = test_df["epss"].values

    results = []
    for t in thresholds:
        y_pred = (epss >= t).astype(int)
        metrics = evaluate(y_true, y_pred, y_prob=epss)
        metrics["threshold"] = t
        metrics["method"] = f"epss_threshold_{t}"
        results.append(metrics)
        print(f"  EPSS >= {t}: F1={metrics['f1']:.3f}, AUC={metrics.get('auc_roc', 'N/A')}")

    return results


def random_baseline(test_df, seed=42):
    """Random baseline: always predict majority class."""
    y_true = test_df["exploited"].values
    majority_class = int(np.bincount(y_true).argmax())

    y_pred = np.full_like(y_true, majority_class)
    metrics = evaluate(y_true, y_pred)
    metrics["method"] = "random_majority"
    metrics["majority_class"] = majority_class

    print(f"  Majority class ({majority_class}): F1={metrics['f1']:.3f}, Acc={metrics['accuracy']:.3f}")
    return [metrics]


def main():
    parser = argparse.ArgumentParser(description="Train baseline models")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--sample-frac", type=float, default=1.0)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading data...")
    train_df, test_df = load_data(sample_frac=args.sample_frac, seed=args.seed)
    print(f"Train: {len(train_df):,} | Test: {len(test_df):,}")
    print(f"Test exploit rate: {test_df['exploited'].mean()*100:.1f}%\n")

    all_results = []

    print("=== CVSS Threshold Baseline ===")
    all_results.extend(cvss_threshold_baseline(test_df))

    print("\n=== EPSS Threshold Baseline ===")
    all_results.extend(epss_threshold_baseline(test_df))

    print("\n=== Random (Majority Class) Baseline ===")
    all_results.extend(random_baseline(test_df, seed=args.seed))

    # Find best baseline
    best = max(all_results, key=lambda r: r.get("auc_roc") or 0)
    print(f"\n=== Best Baseline: {best['method']} (AUC={best.get('auc_roc', 'N/A')}) ===")

    # Save results
    summary = {
        "seed": args.seed,
        "sample_frac": args.sample_frac,
        "date": datetime.now().isoformat(),
        "test_size": len(test_df),
        "test_exploit_rate": float(test_df["exploited"].mean()),
        "baselines": all_results,
        "best_baseline": best,
    }

    out_file = OUTPUT_DIR / f"baselines_seed{args.seed}.json"
    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved: {out_file}")


if __name__ == "__main__":
    main()
