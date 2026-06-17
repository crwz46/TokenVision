import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from tokenvision.analyzer import TokenVision, MetricsEngine, SampleGenerator, Holder, TOKEN_DB
from tokenvision.config import Config
from tokenvision.cache import Cache
from tokenvision.comparison import Comparison
from tokenvision.fetcher import TokenFetcher, TOKEN_CONTRACTS


class TestMetricsEngine:
    def test_top_n(self):
        holders = [Holder("0xA", 100, 50), Holder("0xB", 50, 25),
                   Holder("0xC", 30, 15), Holder("0xD", 20, 10)]
        assert MetricsEngine.top_n_concentration(holders, 2) == 75.0

    def test_hhi(self):
        holders = [Holder("0xA", 60, 60), Holder("0xB", 40, 40)]
        hhi = MetricsEngine.herfindahl_index(holders)
        assert hhi == pytest.approx(0.52, rel=0.01)

    def test_gini_equal(self):
        holders = [Holder("0xA", 100, 50), Holder("0xB", 100, 50)]
        assert MetricsEngine.gini_coefficient(holders) == pytest.approx(0.0, abs=0.01)

    def test_gini_concentrated(self):
        holders = [Holder("0xA", 900, 90), Holder("0xB", 100, 10)]
        gini = MetricsEngine.gini_coefficient(holders)
        assert gini > 0.3

    def test_gini_single(self):
        holders = [Holder("0xA", 100, 100)]
        assert MetricsEngine.gini_coefficient(holders) == pytest.approx(0.0, abs=0.01)

    def test_hhi_monopoly(self):
        holders = [Holder("0xA", 100, 100)]
        assert MetricsEngine.herfindahl_index(holders) == 1.0

    def test_top_n_all(self):
        holders = [Holder(f"0x{i}", i, i) for i in range(10, 0, -1)]
        assert MetricsEngine.top_n_concentration(holders, 10) == pytest.approx(55.0, abs=0.01)

    def test_risk_high(self):
        r, icon = MetricsEngine.risk_level(85, 0.3, 0.95)
        assert "HIGH" in r

    def test_risk_low(self):
        r, icon = MetricsEngine.risk_level(20, 0.02, 0.3)
        assert "LOW" in r

    def test_risk_moderate(self):
        r, icon = MetricsEngine.risk_level(65, 0.15, 0.75)
        assert "MODERATE" in r


class TestSampleGenerator:
    def test_generates_usdc(self):
        ti, holders = SampleGenerator.generate("USDC")
        assert ti.symbol == "USDC"
        assert 1 <= len(holders) <= 100
        assert all(h.percentage > 0 for h in holders)
        assert sum(h.percentage for h in holders) == pytest.approx(100, abs=5)

    def test_deterministic(self):
        _, h1 = SampleGenerator.generate("LINK")
        _, h2 = SampleGenerator.generate("LINK")
        assert h1[0].percentage == h2[0].percentage

    def test_all_tokens(self):
        for sym in TOKEN_DB:
            ti, holders = SampleGenerator.generate(sym)
            assert ti.symbol == sym
            assert len(holders) >= 10

    def test_unknown_token(self):
        ti, holders = SampleGenerator.generate("UNKNOWN")
        assert ti.symbol == "UNKNOWN"
        assert len(holders) > 0

    def test_holder_labels_assigned(self):
        _, holders = SampleGenerator.generate("UNI")
        labels = {h.label for h in holders if h.label}
        assert len(labels) > 0


class TestTokenVision:
    def test_analyze(self):
        tv = TokenVision()
        r = tv.analyze("UNI")
        assert r["token"]["symbol"] == "UNI"
        assert len(r["top_holders"]) == 10
        assert all(k in r["metrics"] for k in
                   ["top10_pct", "hhi", "gini", "risk_label"])

    def test_multiple_tokens(self):
        for sym in ["SHIB", "PEPE", "LINK"]:
            tv = TokenVision()
            r = tv.analyze(sym)
            assert r["token"]["symbol"] == sym

    def test_analyze_live_fallback_to_sample(self):
        tv = TokenVision(use_live=True)
        r = tv.analyze("UNI")
        assert r["token"]["symbol"] == "UNI"
        assert r["metrics"]["total_holders"] > 0

    def test_risk_level_in_report(self):
        tv = TokenVision()
        r = tv.analyze("SHIB")
        assert "risk_label" in r["metrics"]
        assert "risk_icon" in r["metrics"]

    def test_holders_sorted(self):
        tv = TokenVision()
        r = tv.analyze("UNI")
        pcts = [h["percentage"] for h in r["holders"]]
        assert pcts == sorted(pcts, reverse=True)


class TestComparison:
    def test_compare_two_tokens(self):
        reports = Comparison.compare(["UNI", "SHIB"])
        assert len(reports) == 2
        assert reports[0]["token"]["symbol"] == "UNI"
        assert reports[1]["token"]["symbol"] == "SHIB"

    def test_compare_single(self):
        reports = Comparison.compare(["UNI"])
        assert len(reports) == 1

    def test_compare_empty(self):
        reports = Comparison.compare([])
        assert reports == []


class TestFetcher:
    def test_token_contracts_present(self):
        for sym in TOKEN_DB:
            assert sym in TOKEN_CONTRACTS, f"Missing contract for {sym}"

    def test_contract_address_format(self):
        for sym, addr in TOKEN_CONTRACTS.items():
            assert addr.startswith("0x")
            assert len(addr) == 42

    def test_fetcher_no_key_fallback(self):
        fetcher = TokenFetcher()
        result = fetcher.fetch("UNI")
        assert result is None

    def test_fetcher_cache_miss(self):
        cache = Cache(ttl=1)
        assert cache.get("test_nonexistent") is None


class TestConfig:
    def test_default_config(self):
        cfg = Config()
        assert cfg.PORT == 8000
        assert cfg.HOST == "0.0.0.0"
        assert cfg.CACHE_DIR == ".cache"
        assert cfg.CACHE_TTL == 3600

    def test_no_api_key_by_default(self):
        cfg = Config()
        assert not cfg.has_etherscan_key()
        assert not cfg.any_api_key()


class TestCache:
    def test_set_and_get(self):
        cache = Cache(ttl=3600)
        cache.set("test_key", {"foo": "bar"})
        result = cache.get("test_key")
        assert result == {"foo": "bar"}

    def test_cache_expiry(self):
        cache = Cache(ttl=0)
        cache.set("test_expire", "data")
        import time
        time.sleep(0.01)
        assert cache.get("test_expire") is None

    def test_cache_nonexistent(self):
        cache = Cache()
        assert cache.get("__no_such_key__") is None
