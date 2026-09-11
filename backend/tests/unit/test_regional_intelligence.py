"""Unit tests for NewsSense AI Regional Intelligence, Geo-classification,
Importance Scoring, and SSRF Security.
"""

from __future__ import annotations

import pytest

from app.ai.importance_scorer import (
    ImportanceScorer,
    get_importance_scorer,
)
from app.ai.kerala_classifier import (
    DISTRICT_ALIASES,
    KERALA_DISTRICTS,
    KeralaClassifier,
    get_kerala_classifier,
)
from app.pipeline.config.loader import get_config_loader
from app.utils.ssrf_validator import SSRFValidationError, validate_url_ssrf


# ===========================================================================
# 1. Kerala Classifier Tests
# ===========================================================================

def test_kerala_district_direct_mention():
    classifier = get_kerala_classifier()
    result = classifier.classify(
        title="Heavy Monsoon Inundates Ernakulam Low-Lying Areas",
        content="District administration in Ernakulam has declared a holiday for schools as floodwaters entered houses.",
    )
    assert result.is_kerala is True
    assert result.region == "KERALA"
    assert result.district == "Ernakulam"
    assert result.confidence >= 0.85


def test_kerala_district_alias_resolution():
    classifier = get_kerala_classifier()
    # "Cochin" should resolve to canonical "Ernakulam"
    result = classifier.classify(
        title="Smart City Expansion Launched in Cochin",
        content="The IT corridor is set to double in capacity over the next two years.",
    )
    assert result.is_kerala is True
    assert result.region == "KERALA"
    assert result.district == "Ernakulam"

    # "Calicut" should resolve to canonical "Kozhikode"
    result2 = classifier.classify(
        title="New Medical College Campus Inaugurated in Calicut",
        content="Chief Minister dedicated the state-of-the-art super specialty block to the public.",
    )
    assert result2.is_kerala is True
    assert result2.region == "KERALA"
    assert result2.district == "Kozhikode"

    # "Trivandrum" should resolve to "Thiruvananthapuram"
    result3 = classifier.classify(
        title="Secretariat March Planned in Trivandrum Tomorrow",
        content="Traffic diversions will be in place around MG Road.",
    )
    assert result3.is_kerala is True
    assert result3.district == "Thiruvananthapuram"


def test_all_14_kerala_districts_recognized():
    classifier = get_kerala_classifier()
    for district in KERALA_DISTRICTS:
        result = classifier.classify(
            title=f"Development Project Review Meeting in {district}",
            content=f"Officials gathered at the collectorate in {district} to review progress.",
        )
        assert result.is_kerala is True
        assert result.district == district


def test_india_region_classification():
    classifier = get_kerala_classifier()
    result = classifier.classify(
        title="Supreme Court Issues Directives on National Highway Safety in New Delhi",
        content="A bench headed by the Chief Justice of India heard the matter regarding inter-state transit corridors.",
    )
    assert result.is_kerala is False
    assert result.region == "INDIA"


def test_global_region_classification():
    classifier = get_kerala_classifier()
    result = classifier.classify(
        title="Federal Reserve Cuts Benchmark Interest Rate by 25 Basis Points",
        content="Chair Jerome Powell indicated that monetary policy remains calibrated to manage inflation and labor market stability.",
    )
    assert result.is_kerala is False
    assert result.region == "GLOBAL"


# ===========================================================================
# 2. Importance Scorer Tests
# ===========================================================================

def test_importance_scorer_kerala_boost():
    scorer = get_importance_scorer()

    # Identical features except one is Kerala
    score_kerala = scorer.calculate(
        category="disaster",
        source_priority="high",
        source_reliability=0.9,
        independent_source_count=3,
        article_count=5,
        region="KERALA",
    )

    score_global = scorer.calculate(
        category="disaster",
        source_priority="high",
        source_reliability=0.9,
        independent_source_count=3,
        article_count=5,
        region="GLOBAL",
    )

    # Kerala should score higher because Kerala has region_boost=1.20 vs Global 0.85
    assert score_kerala.score > score_global.score
    assert score_kerala.region_boost == 1.20
    assert score_global.region_boost == 0.85


def test_importance_scorer_breaking_classification():
    scorer = get_importance_scorer()

    # High-impact disaster from priority source
    score = scorer.calculate(
        category="disaster",
        source_priority="high",
        source_reliability=0.95,
        independent_source_count=4,
        article_count=8,
        region="KERALA",
        age_hours=0.5,
    )

    assert score.score >= 0.75
    assert score.is_breaking is True
    assert score.urgency_tier in ("CRITICAL", "HIGH")


def test_importance_scorer_low_priority_lifestyle():
    scorer = get_importance_scorer()

    score = scorer.calculate(
        category="lifestyle",
        source_priority="low",
        source_reliability=0.6,
        independent_source_count=1,
        article_count=1,
        region="GLOBAL",
        age_hours=48.0,
    )

    assert score.score < 0.50
    assert score.is_breaking is False
    assert score.urgency_tier == "LOW"


# ===========================================================================
# 3. SSRF Protection Tests
# ===========================================================================

def test_ssrf_validator_blocks_private_ip():
    with pytest.raises(SSRFValidationError):
        validate_url_ssrf("http://192.168.1.100/feed.xml")

    with pytest.raises(SSRFValidationError):
        validate_url_ssrf("http://10.0.0.1/rss")

    with pytest.raises(SSRFValidationError):
        validate_url_ssrf("http://172.16.0.1/news")


def test_ssrf_validator_blocks_localhost():
    with pytest.raises(SSRFValidationError):
        validate_url_ssrf("http://localhost:8000/api/v1/internal")

    with pytest.raises(SSRFValidationError):
        validate_url_ssrf("http://127.0.0.1:6379")


def test_ssrf_validator_blocks_cloud_metadata():
    with pytest.raises(SSRFValidationError):
        validate_url_ssrf("http://169.254.169.254/latest/meta-data/")


def test_ssrf_validator_blocks_bad_schemes():
    with pytest.raises(SSRFValidationError):
        validate_url_ssrf("file:///etc/passwd")

    with pytest.raises(SSRFValidationError):
        validate_url_ssrf("ftp://ftp.example.com/feed")

    with pytest.raises(SSRFValidationError):
        validate_url_ssrf("gopher://127.0.0.1:70")


def test_ssrf_validator_allows_valid_https_url():
    # allow_private=True bypasses DNS resolution for unit test environments
    url = "https://www.thehindu.com/news/national/kerala/feeder/default.rss"
    result = validate_url_ssrf(url, allow_private=True)
    assert result == url


# ===========================================================================
# 4. Sources Registry & Configuration Tests
# ===========================================================================

def test_sources_yaml_loads_kerala_and_india_regions():
    loader = get_config_loader()
    sources = loader.get_all_sources()
    assert len(sources) > 0

    regions = {s.region for s in sources if s.region is not None}
    assert "KERALA" in regions
    assert "INDIA" in regions
    assert "GLOBAL" in regions

    kerala_sources = [s for s in sources if s.region == "KERALA"]
    assert len(kerala_sources) >= 2

    # Verify priority fields
    high_priority = [s for s in sources if s.priority == "high"]
    assert len(high_priority) >= 4
