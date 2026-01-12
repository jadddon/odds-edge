#!/usr/bin/env python3
"""Vegas-Kalshi Value Bet Finder - Compares Vegas odds with Kalshi prediction markets."""

import argparse
import logging
import sys
from datetime import datetime

from api.kalshi_api import KalshiClient
from api.odds_api import OddsAPIClient
from core.value_finder import ValueFinder
from output.console import print_opportunities, print_summary, print_compact_table
from output.csv_export import export_to_csv, export_detailed_csv, append_to_history
from config.settings import TARGET_SPORTS, MIN_NET_EDGE, ODDS_API_KEY, KALSHI_API_KEY


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')


def parse_args():
    parser = argparse.ArgumentParser(description='Find value betting opportunities between Vegas and Kalshi')
    parser.add_argument('--odds-api-key', default=ODDS_API_KEY, help='The Odds API key')
    parser.add_argument('--kalshi-api-key', default=KALSHI_API_KEY, help='Kalshi API key')
    parser.add_argument('--min-edge', type=float, default=MIN_NET_EDGE, help='Minimum net edge threshold')
    parser.add_argument('--min-bookmakers', type=int, default=3, help='Minimum bookmakers for consensus')
    parser.add_argument('--sports', nargs='+', default=['americanfootball_nfl', 'basketball_nba'], help='Sports to analyze')
    parser.add_argument('--all-sports', action='store_true', help='Analyze all supported sports')
    parser.add_argument('--export-csv', action='store_true', help='Export results to CSV')
    parser.add_argument('--detailed-export', action='store_true', help='Export detailed CSV')
    parser.add_argument('--track-history', action='store_true', help='Append to history file')
    parser.add_argument('--compact', action='store_true', help='Use compact table output')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--dry-run', action='store_true', help='Only fetch Kalshi markets (no Vegas API calls)')
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    if not args.odds_api_key and not args.dry_run:
        print("Error: --odds-api-key is required (or set ODDS_API_KEY in .env)")
        sys.exit(1)

    print(f"\n{'=' * 60}")
    print("Vegas-Kalshi Value Bet Finder")
    print(f"Run Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}\n")

    sports = TARGET_SPORTS if args.all_sports else args.sports
    print(f"Analyzing sports: {', '.join(sports)}")
    print(f"Minimum edge threshold: {args.min_edge * 100:.1f}%\n")

    try:
        kalshi_client = KalshiClient(args.kalshi_api_key)
        odds_client = OddsAPIClient(args.odds_api_key) if not args.dry_run else None
    except Exception as e:
        logger.error(f"Failed to initialize API clients: {e}")
        sys.exit(1)

    sport_key_map = {
        'americanfootball_nfl': 'nfl', 'basketball_nba': 'nba', 'icehockey_nhl': 'nhl',
        'baseball_mlb': 'mlb', 'basketball_ncaab': 'ncaab', 'basketball_wncaab': 'ncaaw',
    }
    kalshi_sports = [sport_key_map.get(s, s) for s in sports if s in sport_key_map]

    print("Fetching Kalshi game winner markets...", flush=True)
    try:
        kalshi_markets = kalshi_client.get_game_winner_markets(sports=kalshi_sports, verbose=True)
        print(f"  Total: {len(kalshi_markets)} game winner markets", flush=True)
    except Exception as e:
        logger.error(f"Failed to fetch Kalshi markets: {e}")
        sys.exit(1)

    if args.dry_run:
        print("\n--- Dry Run: Kalshi Game Winner Markets ---")
        for market in kalshi_markets[:20]:
            team = market.get('_team_code', '?')
            price = market.get('yes_ask', 0)
            print(f"  {market.get('ticker')}: {team} @ {price}c")
        if len(kalshi_markets) > 20:
            print(f"  ... and {len(kalshi_markets) - 20} more")
        return

    print("\nFetching Vegas odds...", flush=True)
    vegas_data = {}
    total_events = 0
    for sport in sports:
        try:
            print(f"  - {sport}...", end=" ", flush=True)
            events = odds_client.get_h2h_odds(sport)
            vegas_data[sport] = events
            total_events += len(events)
            print(f"{len(events)} events", flush=True)
        except Exception as e:
            logger.warning(f"Failed to fetch {sport}: {e}")
            vegas_data[sport] = []

    quota = odds_client.get_quota_info()
    if quota['remaining']:
        print(f"\nAPI quota remaining: {quota['remaining']}")

    print("\nAnalyzing for value opportunities...", flush=True)
    finder = ValueFinder(min_edge=args.min_edge, min_bookmakers=args.min_bookmakers)
    all_vegas_events = [e for events in vegas_data.values() for e in events]
    all_opportunities = finder.find_game_winner_value(all_vegas_events, kalshi_markets, verbose=args.verbose)

    if args.compact:
        print_compact_table(all_opportunities)
    else:
        print_opportunities(all_opportunities)

    print_summary(total_events, len(kalshi_markets), all_opportunities)

    if args.export_csv and all_opportunities:
        export_to_csv(all_opportunities)
    if args.detailed_export and all_opportunities:
        export_detailed_csv(all_opportunities)
    if args.track_history and all_opportunities:
        append_to_history(all_opportunities)

    return 0 if all_opportunities else 1


if __name__ == '__main__':
    sys.exit(main())
