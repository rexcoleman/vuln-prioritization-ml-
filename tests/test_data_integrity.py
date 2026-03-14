"""Data integrity tests for vulnerability prioritization project.

LT-1: No future data leakage (temporal split enforced)
LT-2: No label leakage (exploited status not in features)
LT-3: Join integrity (CVE IDs match across sources)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


DATA_DIR = Path("data/processed")
SPLITS_DIR = Path("data/splits")


@pytest.fixture
def train_df():
    path = DATA_DIR / "train.parquet"
    if not path.exists():
        pytest.skip("Train data not yet built")
    return pd.read_parquet(path)


@pytest.fixture
def test_df():
    path = DATA_DIR / "test.parquet"
    if not path.exists():
        pytest.skip("Test data not yet built")
    return pd.read_parquet(path)


@pytest.fixture
def feature_cols():
    path = DATA_DIR / "feature_cols.json"
    if not path.exists():
        pytest.skip("Feature cols not yet built")
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def split_info():
    path = SPLITS_DIR / "split_info.json"
    if not path.exists():
        pytest.skip("Split info not yet created")
    with open(path) as f:
        return json.load(f)


# --- LT-1: Temporal leakage ---

class TestTemporalLeakage:
    """No future data in training set."""

    def test_train_before_split_year(self, train_df, split_info):
        """All training CVEs published before split year."""
        split_year = split_info["split_year"]
        assert train_df["pub_year"].max() < split_year, \
            f"Train contains CVEs from {train_df['pub_year'].max()}, expected < {split_year}"

    def test_test_after_split_year(self, test_df, split_info):
        """All test CVEs published in or after split year."""
        split_year = split_info["split_year"]
        assert test_df["pub_year"].min() >= split_year, \
            f"Test contains CVEs from {test_df['pub_year'].min()}, expected >= {split_year}"

    def test_no_overlap(self, train_df, test_df):
        """No CVE appears in both train and test."""
        overlap = set(train_df["cve_id"]) & set(test_df["cve_id"])
        assert len(overlap) == 0, f"Found {len(overlap)} CVEs in both train and test"


# --- LT-2: Label leakage ---

class TestLabelLeakage:
    """Exploited label not leaked into features."""

    def test_exploited_not_in_features(self, feature_cols):
        """'exploited' column not in feature list."""
        assert "exploited" not in feature_cols, "'exploited' is in feature columns"

    def test_no_cve_id_in_features(self, feature_cols):
        """CVE ID not in feature list (would be a perfect predictor via lookup)."""
        assert "cve_id" not in feature_cols, "'cve_id' is in feature columns"

    def test_no_description_in_features(self, feature_cols):
        """Raw description text not in feature list (use TF-IDF/keywords instead)."""
        assert "description" not in feature_cols, "'description' is in feature columns"


# --- LT-3: Join integrity ---

class TestJoinIntegrity:
    """Data joins are correct."""

    def test_no_null_labels(self, train_df, test_df):
        """Every CVE has an exploited label (0 or 1)."""
        assert train_df["exploited"].isna().sum() == 0, "Null labels in train"
        assert test_df["exploited"].isna().sum() == 0, "Null labels in test"

    def test_label_is_binary(self, train_df, test_df):
        """Label is strictly 0 or 1."""
        assert set(train_df["exploited"].unique()).issubset({0, 1})
        assert set(test_df["exploited"].unique()).issubset({0, 1})

    def test_cve_ids_are_unique(self, train_df, test_df):
        """No duplicate CVE IDs within train or test."""
        assert train_df["cve_id"].is_unique, \
            f"Duplicate CVEs in train: {train_df['cve_id'].duplicated().sum()}"
        assert test_df["cve_id"].is_unique, \
            f"Duplicate CVEs in test: {test_df['cve_id'].duplicated().sum()}"


# --- Sanity checks ---

class TestSanityChecks:
    """Basic data sanity."""

    def test_train_has_both_classes(self, train_df):
        """Training data has both exploited and non-exploited CVEs."""
        assert train_df["exploited"].sum() > 0, "No exploited CVEs in train"
        assert (train_df["exploited"] == 0).sum() > 0, "No non-exploited CVEs in train"

    def test_test_has_both_classes(self, test_df):
        """Test data has both exploited and non-exploited CVEs."""
        assert test_df["exploited"].sum() > 0, "No exploited CVEs in test"
        assert (test_df["exploited"] == 0).sum() > 0, "No non-exploited CVEs in test"

    def test_feature_cols_nonempty(self, feature_cols):
        """Feature list is non-empty."""
        assert len(feature_cols) > 10, f"Only {len(feature_cols)} features — expected more"

    def test_no_all_null_features(self, train_df, feature_cols):
        """No feature column is entirely null."""
        for col in feature_cols:
            if col in train_df.columns:
                assert train_df[col].notna().any(), f"Feature {col} is all null"

    def test_split_hashes_match(self, split_info):
        """Split info file contains valid hashes."""
        assert len(split_info["train_index_hash"]) == 64, "Invalid train hash"
        assert len(split_info["test_index_hash"]) == 64, "Invalid test hash"
