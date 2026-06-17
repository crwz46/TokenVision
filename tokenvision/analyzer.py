import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


TOKEN_DB = {
    "USDC":  {"name": "USD Coin",        "supply": 30_000_000_000,       "decimals": 6},
    "USDT":  {"name": "Tether",          "supply": 80_000_000_000,       "decimals": 6},
    "LINK":  {"name": "Chainlink",       "supply": 600_000_000,         "decimals": 18},
    "UNI":   {"name": "Uniswap",         "supply": 1_000_000_000,       "decimals": 18},
    "AAVE":  {"name": "Aave",            "supply": 16_000_000,          "decimals": 18},
    "MATIC": {"name": "Polygon",         "supply": 10_000_000_000,      "decimals": 18},
    "SHIB":  {"name": "Shiba Inu",       "supply": 589_000_000_000_000, "decimals": 18},
    "PEPE":  {"name": "Pepe",            "supply": 420_000_000_000_000, "decimals": 18},
    "WETH":  {"name": "Wrapped Ether",   "supply": 3_500_000,           "decimals": 18},
    "CRO":   {"name": "Cronos",          "supply": 30_000_000_000,      "decimals": 8},
}


@dataclass
class Holder:
    address: str
    balance: float
    percentage: float
    label: str = ""


@dataclass
class TokenInfo:
    symbol: str
    name: str
    decimals: int
    total_supply: float


class MetricsEngine:
    @staticmethod
    def top_n_concentration(holders: List[Holder], n: int = 10) -> float:
        top = sorted(holders, key=lambda h: h.percentage, reverse=True)[:n]
        return round(sum(h.percentage for h in top), 2)

    @staticmethod
    def herfindahl_index(holders: List[Holder]) -> float:
        shares = [h.percentage / 100 for h in holders]
        return round(sum(s * s for s in shares), 4)

    @staticmethod
    def gini_coefficient(holders: List[Holder]) -> float:
        values = sorted([h.balance for h in holders])
        n = len(values)
        if n == 0 or sum(values) == 0:
            return 0.0
        cum_sum = sum(i * v for i, v in enumerate(values, 1))
        gini = (2 * cum_sum) / (n * sum(values)) - (n + 1) / n
        return round(gini, 4)

    @staticmethod
    def risk_level(top10_pct: float, hhi: float, gini: float) -> Tuple[str, str]:
        score = 0
        if top10_pct > 80: score += 3
        elif top10_pct > 60: score += 2
        elif top10_pct > 40: score += 1
        if hhi > 0.2: score += 3
        elif hhi > 0.1: score += 2
        elif hhi > 0.05: score += 1
        if gini > 0.9: score += 3
        elif gini > 0.8: score += 2
        elif gini > 0.7: score += 1
        if score >= 7: return "HIGH CONCENTRATION", "🔴"
        elif score >= 4: return "MODERATE CONCENTRATION", "🟡"
        return "LOW CONCENTRATION", "🟢"


class SampleGenerator:
    @staticmethod
    def generate(symbol: str) -> Tuple[TokenInfo, List[Holder]]:
        info = TOKEN_DB.get(symbol.upper(), {
            "name": symbol.upper(), "supply": 1_000_000_000, "decimals": 18
        })
        ti = TokenInfo(symbol.upper(), info["name"], info["decimals"], info["supply"])
        random.seed(hash(symbol))

        holders = []
        whale_shares = [random.uniform(8, 25) for _ in range(5)]
        scale = random.uniform(40, 65) / sum(whale_shares)
        whale_shares = [s * scale for s in whale_shares]

        for i, share in enumerate(whale_shares[:5]):
            holders.append(Holder(
                address=f"0x{random.randint(10**39, 10**40-1):040x}",
                balance=info["supply"] * share / 100,
                percentage=share,
                label=["🐋 Whale", "🐳 Mega Whale", "🦈 Shark", "Whale", "Whale"][i],
            ))

        remaining = 100 - sum(whale_shares)
        for _ in range(random.randint(8, 15)):
            share = random.uniform(0.5, min(5, remaining))
            remaining -= share
            holders.append(Holder(
                address=f"0x{random.randint(10**39, 10**40-1):040x}",
                balance=info["supply"] * share / 100,
                percentage=share,
            ))

        while remaining > 0.01 and len(holders) < 100:
            share = random.uniform(0.01, min(1, remaining))
            remaining -= share
            holders.append(Holder(
                address=f"0x{random.randint(10**39, 10**40-1):040x}",
                balance=info["supply"] * share / 100,
                percentage=share,
            ))

        if remaining > 0 and holders:
            holders[-1].percentage += remaining
            holders[-1].balance += info["supply"] * remaining / 100

        holders.sort(key=lambda h: h.balance, reverse=True)
        return ti, holders[:100]


class TokenVision:
    def __init__(self, use_live: bool = False):
        self.token: Optional[TokenInfo] = None
        self.holders: List[Holder] = []
        self.metrics: Dict = {}
        self.use_live = use_live
        self._live_source = False

    def analyze(self, symbol: str = "UNI") -> Dict:
        if self.use_live:
            from .config import Config
            from .fetcher import TokenFetcher
            config = Config()
            if config.any_api_key():
                fetcher = TokenFetcher(config)
                result = fetcher.fetch(symbol)
                if result:
                    self.token, self.holders = result
                    self._live_source = True
                    self._compute_metrics()
                    return self._report()
        self.token, self.holders = SampleGenerator.generate(symbol)
        self._compute_metrics()
        return self._report()

    def _compute_metrics(self):
        h = self.holders
        if not h:
            self.metrics = {}
            return
        top10 = MetricsEngine.top_n_concentration(h, 10)
        top5 = MetricsEngine.top_n_concentration(h, 5)
        top1 = h[0].percentage
        hhi = MetricsEngine.herfindahl_index(h)
        gini = MetricsEngine.gini_coefficient(h)
        risk, icon = MetricsEngine.risk_level(top10, hhi, gini)
        eff_n = round(1 / hhi, 1) if hhi > 0 else len(h)

        self.metrics = {
            "total_holders": len(h),
            "top1_pct": top1,
            "top5_pct": top5,
            "top10_pct": top10,
            "hhi": hhi,
            "gini": gini,
            "effective_holders": eff_n,
            "risk_label": risk,
            "risk_icon": icon,
        }

    def _report(self) -> Dict:
        return {
            "token": {
                "symbol": self.token.symbol,
                "name": self.token.name,
                "total_supply": int(self.token.total_supply),
                "decimals": self.token.decimals,
            },
            "metrics": self.metrics,
            "top_holders": [
                {
                    "rank": i + 1,
                    "address": h.address,
                    "balance": h.balance,
                    "percentage": round(h.percentage, 2),
                    "label": h.label,
                }
                for i, h in enumerate(self.holders[:10])
            ],
            "holders": [
                {
                    "rank": i + 1,
                    "address": h.address,
                    "balance": h.balance,
                    "percentage": round(h.percentage, 2),
                    "label": h.label,
                }
                for i, h in enumerate(self.holders)
            ],
        }

    @staticmethod
    def display(report: Dict, live: bool = False):
        t = report["token"]
        m = report["metrics"]

        source = "🔴 LIVE" if live else "🔵 SAMPLE"
        print("=" * 70)
        print(f"  {m['risk_icon']} TOKENVISION — {t['symbol']}  ({source})")
        print("=" * 70)
        print(f"\n  Token       : {t['name']} ({t['symbol']})")
        print(f"  Supply      : {t['total_supply']:,}")

        print(f"\n  {'─' * 40}")
        print(f"  CONCENTRATION")
        print(f"  {'─' * 40}")
        print(f"  Top 1       : {m['top1_pct']:>6.2f}%")
        print(f"  Top 5       : {m['top5_pct']:>6.2f}%")
        print(f"  Top 10      : {m['top10_pct']:>6.2f}%")
        print(f"  HHI         : {m['hhi']:>8.4f}")
        print(f"  Gini        : {m['gini']:>8.4f}")
        print(f"  Eff. Holders: {m['effective_holders']:>8.1f}")

        risk_icon = m['risk_icon']
        risk_label = m['risk_label']
        print(f"\n  Risk        : {risk_icon} {risk_label}")

        print(f"\n  TOP 10:")
        print(f"  {'Rank':5s} {'Address':44s} {'Hold':>8s} {'Label':>10s}")
        print(f"  {'─' * 5} {'─' * 44} {'─' * 8} {'─' * 10}")

        for h in report["top_holders"]:
            addr_short = f"{h['address'][:6]}...{h['address'][-4:]}"
            print(f"  {h['rank']:4d}. {addr_short:42s} "
                  f"{h['percentage']:>6.2f}%  {h['label']:>10s}")

        print("=" * 70)
        if "HIGH" in risk_label:
            print("  ⚠️  High centralization risk. Price sensitive to whale moves.")
        elif "MODERATE" in risk_label:
            print("  📊 Moderate concentration. Some whale influence.")
        else:
            print("  ✅ Well distributed. Low centralization risk.")
        print("=" * 70)
