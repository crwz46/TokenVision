import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from tokenvision.analyzer import TokenVision, MetricsEngine, SampleGenerator, Holder, TOKEN_DB


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

    def test_risk_high(self):
        r, icon = MetricsEngine.risk_level(85, 0.3, 0.95)
        assert "HIGH" in r

    def test_risk_low(self):
        r, icon = MetricsEngine.risk_level(20, 0.02, 0.3)
        assert "LOW" in r


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
