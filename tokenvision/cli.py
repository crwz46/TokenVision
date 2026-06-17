import sys
import argparse

from .analyzer import TokenVision


def main():
    parser = argparse.ArgumentParser(
        description="TokenVision — Token Holder Concentration Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tokenvision UNI                      Analyze UNI holder concentration
  tokenvision SHIB --charts            Analyze with charts
  tokenvision UNI --live               Use Etherscan live data
  tokenvision --compare UNI SHIB PEPE  Compare multiple tokens
  tokenvision --server                 Start FastAPI web server
  tokenvision --list                   Show available tokens
        """,
    )
    parser.add_argument("symbol", nargs="?", help="Token symbol")
    parser.add_argument("--charts", action="store_true", help="Generate charts")
    parser.add_argument("--live", action="store_true", help="Use Etherscan live data")
    parser.add_argument("--compare", nargs="+", metavar="SYM", help="Compare multiple tokens")
    parser.add_argument("--server", action="store_true", help="Start FastAPI web server")
    parser.add_argument("--list", action="store_true", help="List available tokens")

    args = parser.parse_args()

    if args.server:
        start_server()
        return

    if args.list:
        from .analyzer import TOKEN_DB
        print("\n  Available tokens:\n")
        for sym, info in sorted(TOKEN_DB.items()):
            print(f"  {sym:6s} — {info['name']}")
        print()
        return

    if args.compare:
        from .comparison import Comparison
        Comparison.compare_and_display(args.compare, live=args.live)
        return

    if not args.symbol:
        parser.print_help()
        return

    tv = TokenVision(use_live=args.live)
    report = tv.analyze(args.symbol.upper())
    TokenVision.display(report, live=tv._live_source)

    if args.charts:
        from .charts import generate
        generate(report)


def start_server():
    try:
        import uvicorn
        from .config import Config
        cfg = Config()
        print(f"\n  🚀 TokenVision API running at http://{cfg.HOST}:{cfg.PORT}")
        print(f"  📖 Docs at http://{cfg.HOST if cfg.HOST != '0.0.0.0' else 'localhost'}:{cfg.PORT}/docs\n")
        uvicorn.run("tokenvision.api:app", host=cfg.HOST, port=cfg.PORT, log_level="info")
    except ImportError:
        print("pip install 'tokenvision[server]'")
        sys.exit(1)


def run():
    main()


if __name__ == "__main__":
    main()
