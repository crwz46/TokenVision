import sys
import argparse

from .analyzer import TokenVision


def main():
    parser = argparse.ArgumentParser(
        description="TokenVision — Token Holder Concentration Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tokenvision UNI              Analyze UNI holder concentration
  tokenvision SHIB             Analyze SHIB holders
  tokenvision PEPE --charts    Generate matplotlib charts
  tokenvision --list           Show available tokens
        """,
    )
    parser.add_argument("symbol", nargs="?", default="UNI", help="Token symbol")
    parser.add_argument("--charts", action="store_true", help="Generate charts")
    parser.add_argument("--list", action="store_true", help="List available tokens")

    args = parser.parse_args()

    if args.list:
        from .analyzer import TOKEN_DB
        print("\n  Available tokens:\n")
        for sym, info in sorted(TOKEN_DB.items()):
            print(f"  {sym:6s} — {info['name']}")
        print()
        return

    tv = TokenVision()
    report = tv.analyze(args.symbol.upper())
    TokenVision.display(report)

    if args.charts:
        from .charts import generate
        generate(report)


def run():
    main()


if __name__ == "__main__":
    main()
