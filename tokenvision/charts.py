import os
from typing import Dict


CHARTS_DIR = "charts"
EXPORT_FORMATS = ["png", "pdf", "svg"]


def generate(report: Dict, formats: list = None) -> Dict[str, str]:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("pip install matplotlib")
        return {}

    os.makedirs(CHARTS_DIR, exist_ok=True)
    symbol = report["token"]["symbol"]
    paths = {}

    if formats is None:
        formats = ["png"]

    # Pie chart
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    top10 = report["top_holders"]
    others = 100 - sum(h["percentage"] for h in top10)
    labels = [f"{h['address'][:6]}..{h['address'][-4:]}" for h in top10] + ["Others"]
    sizes = [h["percentage"] for h in top10] + [max(0, others)]
    colors = ["#ff6b6b","#ffd93d","#6bcb77","#4d96ff","#ff8fab",
              "#845ef7","#36d399","#f59e0b","#ef4444","#8b5cf6","#374151"]

    wedges, texts, autotexts = ax.pie(
        sizes, labels=None, autopct="%1.1f%%", startangle=90,
        colors=colors[:len(sizes)],
        textprops={"color": "#c9d1d9", "fontsize": 9}, pctdistance=0.75,
    )
    for at in autotexts:
        at.set_color("#c9d1d9")
        at.set_fontsize(8)

    ax.legend(wedges, labels, title="Top 10 Holders",
              loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
              fontsize=8, facecolor="#161b22", edgecolor="#30363d",
              labelcolor="#c9d1d9")
    ax.set_title(f"{symbol} Holder Distribution", color="#58a6ff",
                  fontsize=14, fontweight="bold", pad=20)

    for fmt in formats:
        p = os.path.join(CHARTS_DIR, f"{symbol}_pie.{fmt}")
        plt.tight_layout()
        plt.savefig(p, dpi=150, bbox_inches="tight", facecolor="#0d1117")
        paths[f"pie_{fmt}"] = p
    plt.close()

    # Bar chart
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    top20 = report["holders"][:20]
    addrs = [f"{h['address'][:4]}..{h['address'][-4:]}" for h in top20]
    pcts = [h["percentage"] for h in top20]

    bars = ax.barh(range(len(addrs)), pcts, color="#58a6ff",
                    edgecolor="#1f6feb", height=0.7)
    ax.set_yticks(range(len(addrs)))
    ax.set_yticklabels(addrs, fontsize=8, color="#c9d1d9")
    ax.invert_yaxis()
    ax.set_xlabel("Holding %", color="#8b949e", fontsize=10)
    ax.set_title(f"{symbol} — Top 20", color="#58a6ff", fontsize=14, fontweight="bold")

    ax.spines["bottom"].set_color("#30363d")
    ax.spines["left"].set_color("#30363d")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors="#8b949e")
    ax.grid(axis="x", color="#21262d", linewidth=0.5)

    for bar, pct in zip(bars, pcts):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{pct:.2f}%", va="center", fontsize=8, color="#c9d1d9")

    for fmt in formats:
        p = os.path.join(CHARTS_DIR, f"{symbol}_bar.{fmt}")
        plt.tight_layout()
        plt.savefig(p, dpi=150, bbox_inches="tight", facecolor="#0d1117")
        paths[f"bar_{fmt}"] = p
    plt.close()

    # Lorenz curve
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    balances = sorted([h["balance"] for h in report["holders"]])
    n = len(balances)
    if n > 0:
        cum = [0]
        total = sum(balances) or 1
        running = 0
        for b in balances:
            running += b
            cum.append(running / total)
        pop = [i / n for i in range(n + 1)]
        ax.plot(pop, cum, color="#6bcb77", linewidth=2.5, label="Distribution")
        ax.plot([0, 1], [0, 1], color="#ff6b6b", linewidth=1.5,
                linestyle="--", label="Equality")
        gini = report["metrics"]["gini"]
        ax.fill_between(pop, pop, cum, alpha=0.1, color="#6bcb77",
                        label=f"Gini = {gini}")

    ax.set_xlabel("Population %", color="#8b949e", fontsize=10)
    ax.set_ylabel("Cumulative Holdings %", color="#8b949e", fontsize=10)
    ax.set_title("Lorenz Curve", color="#58a6ff", fontsize=14, fontweight="bold")
    ax.legend(fontsize=10, facecolor="#161b22", edgecolor="#30363d",
              labelcolor="#c9d1d9")
    ax.spines["bottom"].set_color("#30363d")
    ax.spines["left"].set_color("#30363d")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors="#8b949e")
    ax.grid(color="#21262d", linewidth=0.5, alpha=0.5)

    for fmt in formats:
        p = os.path.join(CHARTS_DIR, f"{symbol}_lorenz.{fmt}")
        plt.tight_layout()
        plt.savefig(p, dpi=150, bbox_inches="tight", facecolor="#0d1117")
        paths[f"lorenz_{fmt}"] = p
    plt.close()

    print(f"\n  Charts saved to {CHARTS_DIR}/")
    return paths
