#!/usr/bin/env python3
"""
O.M.N.I.S — Operational Multi-Node Intelligence System
CLI entry point.

Usage:
    python omnis.py "example.com"
    python omnis.py "example.com" --disciplines osint cybint sigint
    python omnis.py "example.com" --query "Investiga presencia en redes y amenazas CTI"
    python omnis.py --list-disciplines
"""
import sys
import os

# ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
from datetime import datetime, timezone

from core.orchestrator import Orchestrator, DISCIPLINE_MODULES

BANNER = r"""
   ██████╗ ███╗   ███╗███╗   ██╗██╗███████╗
  ██╔═══██╗████╗ ████║████╗  ██║██║██╔════╝
  ██║   ██║██╔████╔██║██╔██╗ ██║██║███████╗
  ██║   ██║██║╚██╔╝██║██║╚██╗██║██║╚════██║
  ╚██████╔╝██║ ╚═╝ ██║██║ ╚████║██║███████║
   ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝╚══════╝

    Operational Multi-Node Intelligence System
           "See all. Connect all. Understand all."
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="omnis",
        description="O.M.N.I.S — Operational Multi-Node Intelligence System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python omnis.py example.com
  python omnis.py example.com --disciplines osint cybint sigint
  python omnis.py 1.2.3.4 --disciplines osint cybint sigint darkint
  python omnis.py "Acme Corp" --disciplines osint socmint finint
        """,
    )
    parser.add_argument("target", nargs="?", help="Investigation target (domain, IP, username, company name)")
    parser.add_argument("--query", "-q", default="", help="Natural language query/context for the investigation")
    parser.add_argument(
        "--disciplines", "-d",
        nargs="+",
        choices=list(DISCIPLINE_MODULES.keys()),
        default=None,
        help="Limit to specific disciplines (default: all)",
    )
    parser.add_argument("--output", "-o", help="Save report to file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--list-disciplines", action="store_true", help="List available disciplines and exit")
    return parser.parse_args()


def main() -> None:
    print(BANNER)

    args = parse_args()

    if args.list_disciplines:
        print("Available disciplines:")
        for key in DISCIPLINE_MODULES:
            print(f"  {key}")
        return

    if not args.target:
        print("Error: target is required. Use --help for usage.")
        sys.exit(1)

    query = args.query or f"OMNIS: Investiga {args.target}"
    print(f"[*] Target   : {args.target}")
    print(f"[*] Query    : {query}")
    print(f"[*] Disciplines: {', '.join(args.disciplines or list(DISCIPLINE_MODULES.keys()))}")
    print(f"[*] Started  : {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print()

    orchestrator = Orchestrator(disciplines=args.disciplines, verbose=args.verbose)
    report = orchestrator.investigate(query=query, target=args.target)

    print(report)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n[+] Report saved to: {args.output}")


if __name__ == "__main__":
    main()
