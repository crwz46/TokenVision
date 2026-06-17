from typing import Dict, List

from .analyzer import TokenVision


class Comparison:
    @staticmethod
    def compare(symbols: List[str], live: bool = False) -> List[Dict]:
        reports = []
        for sym in symbols:
            tv = TokenVision(use_live=live)
            report = tv.analyze(sym.upper())
            reports.append(report)
        return reports

    @staticmethod
    def display(reports: List[Dict]):
        if not reports:
            print("No data to compare.")
            return

        print()
        print(f"  {'Symbol':7s} {'Name':14s} {'Holders':>8s} {'Top 1':>8s} {'Top 5':>8s} {'Top 10':>9s} {'HHI':>8s} {'Gini':>8s} {'Risk':>16s}")
        print(f"  {'─' * 7} {'─' * 14} {'─' * 8} {'─' * 8} {'─' * 8} {'─' * 9} {'─' * 8} {'─' * 8} {'─' * 16}")

        for r in reports:
            t = r["token"]
            m = r["metrics"]
            risk_short = f"{m['risk_icon']} {m['risk_label'][:12]}"
            print(f"  {t['symbol']:7s} {t['name']:14s} {m['total_holders']:>8d} "
                  f"{m['top1_pct']:>6.2f}%  {m['top5_pct']:>6.2f}%  {m['top10_pct']:>7.2f}%  "
                  f"{m['hhi']:>6.4f}  {m['gini']:>6.4f}  {risk_short:>16s}")

        print()

    @staticmethod
    def compare_and_display(symbols: List[str], live: bool = False):
        reports = Comparison.compare(symbols, live)
        Comparison.display(reports)
        return reports
