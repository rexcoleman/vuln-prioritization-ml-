"""Script import and basic functionality tests.

These tests verify scripts can be imported without errors
and that key functions exist. They don't require data.
"""
import importlib
import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestScriptImports:
    """All scripts import without error."""

    def test_import_ingest_nvd(self):
        mod = importlib.import_module("scripts.ingest_nvd")
        assert hasattr(mod, "check_api_access")
        assert hasattr(mod, "ingest_nvd")

    def test_import_ingest_exploitdb(self):
        mod = importlib.import_module("scripts.ingest_exploitdb")
        assert hasattr(mod, "check_access")
        assert hasattr(mod, "ingest_exploitdb")

    def test_import_ingest_epss(self):
        mod = importlib.import_module("scripts.ingest_epss")
        assert hasattr(mod, "check_access")
        assert hasattr(mod, "ingest_epss")

    def test_import_build_features(self):
        mod = importlib.import_module("scripts.build_features")
        assert hasattr(mod, "load_nvd_cves")
        assert hasattr(mod, "engineer_features")
        assert hasattr(mod, "create_temporal_split")
        assert hasattr(mod, "parse_cvss_vector")

    def test_import_train_baselines(self):
        mod = importlib.import_module("scripts.train_baselines")
        assert hasattr(mod, "cvss_threshold_baseline")
        assert hasattr(mod, "epss_threshold_baseline")
        assert hasattr(mod, "evaluate")

    def test_import_train_models(self):
        mod = importlib.import_module("scripts.train_models")
        assert hasattr(mod, "train_random_forest")
        assert hasattr(mod, "train_xgboost")
        assert hasattr(mod, "train_logistic_regression")

    def test_import_check_data_ready(self):
        mod = importlib.import_module("scripts.check_data_ready")
        assert hasattr(mod, "check_exploitdb")
        assert hasattr(mod, "check_epss")
        assert hasattr(mod, "check_nvd")


class TestCVSSVectorParsing:
    """Test CVSS vector string parsing (no data needed)."""

    def test_parse_valid_v31(self):
        from scripts.build_features import parse_cvss_vector
        result = parse_cvss_vector("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
        assert result["cvss_av"] == "N"
        assert result["cvss_ac"] == "L"
        assert result["cvss_pr"] == "N"
        assert result["cvss_c"] == "H"

    def test_parse_empty_string(self):
        from scripts.build_features import parse_cvss_vector
        result = parse_cvss_vector("")
        assert result == {}

    def test_parse_none(self):
        from scripts.build_features import parse_cvss_vector
        result = parse_cvss_vector(None)
        assert result == {}

    def test_parse_v2_style(self):
        from scripts.build_features import parse_cvss_vector
        # v2 vectors have different format but parser should handle gracefully
        result = parse_cvss_vector("AV:N/AC:L/Au:N/C:P/I:P/A:P")
        assert "cvss_av" in result or result == {}  # Either parses or returns empty
