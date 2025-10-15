"""Cross-System Event Correlator module."""

from __future__ import annotations

import argparse
import json
import sys

from .correlate import build_chains, format_json, format_text
from .parsers import ParseReport, parse_api, parse_db, parse_storage


def main(argv=None):
    """

    Args:
      argv: (Default value = None)

    Returns:

    """
    parser = argparse.ArgumentParser(
        prog="correlator", description="Cross-System Event Correlator"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    c = sub.add_parser("correlate", help="Parse logs and correlate events")
    c.add_argument("--api", required=False, help="Path to api.log")
    c.add_argument("--db", required=False, help="Path to db.log")
    c.add_argument("--storage", required=False, help="Path to storage.log")
    c.add_argument(
        "--date", required=False, help="Assumed date for DB times, e.g., 2025-09-30"
    )
    c.add_argument(
        "--window", type=int, default=60, help="Correlation window in seconds"
    )
    c.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    c.add_argument(
        "--show-orphans",
        action="store_true",
        help="Also print orphans and parse errors",
    )

    args = parser.parse_args(argv)

    if args.command == "correlate":
        report = ParseReport()
        events = []
        if args.api:
            events += parse_api(args.api, report)
        if args.db:
            events += parse_db(args.db, report, assumed_date=args.date)
        if args.storage:
            events += parse_storage(args.storage, report)
        if not events:
            print("No events parsed. Provide at least one log file.", file=sys.stderr)
            sys.exit(2)

        chains, orphans = build_chains(events, window_sec=args.window)
        if args.format == "text":
            print(format_text(chains))
            if args.show_orphans:
                print("=== ORPHANS ===")
                for e in sorted(orphans, key=lambda x: x.ts):
                    print(
                        f"{e.ts.isoformat()} {e.source} {e.actor} :: {e.action} :: {e.meta}"
                    )
                if report.errors:
                    print("\n=== PARSE ERRORS ===")
                    for err in report.errors:
                        print(err)
        else:
            obj = {"chains": format_json(chains)}
            if args.show_orphans:
                obj["orphans"] = [
                    {
                        "timestamp": e.ts.isoformat(),
                        "source": e.source,
                        "actor": e.actor,
                        "action": e.action,
                        "meta": e.meta,
                    }
                    for e in orphans
                ]
                obj["parse_errors"] = report.errors
            print(json.dumps(obj, indent=2))


if __name__ == "__main__":
    main()
