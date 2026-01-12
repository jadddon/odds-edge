"""CSV export functionality for value bet opportunities."""

import csv
import os
from datetime import datetime
from typing import List, Optional
from models.opportunity import ValueOpportunity
from config.settings import EXPORT_PATH


def ensure_export_directory():
    if not os.path.exists(EXPORT_PATH):
        os.makedirs(EXPORT_PATH)


def export_to_csv(opportunities: List[ValueOpportunity], filename: Optional[str] = None) -> str:
    """Export opportunities to CSV file."""
    ensure_export_directory()
    if filename is None:
        filename = f"value_bets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(EXPORT_PATH, filename)

    fieldnames = ['sport', 'home_team', 'away_team', 'kalshi_ticker', 'vegas_home_prob',
                  'vegas_away_prob', 'kalshi_home_price', 'kalshi_away_price',
                  'recommended_position', 'recommended_team', 'gross_edge', 'net_edge',
                  'fee_impact', 'ev_per_contract', 'ev_100_contracts', 'num_bookmakers', 'confidence']

    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for opp in opportunities:
            writer.writerow({
                'sport': opp.sport,
                'home_team': opp.home_team,
                'away_team': opp.away_team,
                'kalshi_ticker': opp.kalshi_ticker,
                'vegas_home_prob': f"{opp.vegas_home_prob:.4f}",
                'vegas_away_prob': f"{opp.vegas_away_prob:.4f}",
                'kalshi_home_price': f"{opp.kalshi_home_price:.2f}",
                'kalshi_away_price': f"{opp.kalshi_away_price:.2f}",
                'recommended_position': opp.recommended_position,
                'recommended_team': opp.recommended_team,
                'gross_edge': f"{opp.gross_edge:.4f}",
                'net_edge': f"{opp.net_edge:.4f}",
                'fee_impact': f"{opp.fee_impact:.4f}",
                'ev_per_contract': f"{opp.expected_value_per_contract:.4f}",
                'ev_100_contracts': f"{opp.expected_value_100_contracts:.2f}",
                'num_bookmakers': opp.num_bookmakers,
                'confidence': opp.confidence
            })

    print(f"Exported {len(opportunities)} opportunities to {filepath}")
    return filepath


def export_detailed_csv(opportunities: List[ValueOpportunity], filename: Optional[str] = None) -> str:
    """Export opportunities with additional calculated fields."""
    ensure_export_directory()
    if filename is None:
        filename = f"value_bets_detailed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(EXPORT_PATH, filename)

    fieldnames = ['timestamp', 'sport', 'matchup', 'kalshi_ticker', 'recommendation',
                  'net_edge_pct', 'ev_100_contracts', 'num_bookmakers', 'confidence']
    timestamp = datetime.now().isoformat()

    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for opp in opportunities:
            writer.writerow({
                'timestamp': timestamp,
                'sport': opp.sport,
                'matchup': f"{opp.away_team} @ {opp.home_team}",
                'kalshi_ticker': opp.kalshi_ticker,
                'recommendation': opp.display_position,
                'net_edge_pct': f"{opp.net_edge:.2%}",
                'ev_100_contracts': f"${opp.expected_value_100_contracts:.2f}",
                'num_bookmakers': opp.num_bookmakers,
                'confidence': opp.confidence.upper()
            })

    print(f"Exported detailed report to {filepath}")
    return filepath


def append_to_history(opportunities: List[ValueOpportunity], filename: str = "opportunity_history.csv"):
    """Append opportunities to historical tracking file."""
    ensure_export_directory()
    filepath = os.path.join(EXPORT_PATH, filename)
    file_exists = os.path.exists(filepath)

    fieldnames = ['scan_timestamp', 'sport', 'home_team', 'away_team', 'kalshi_ticker',
                  'recommended_position', 'net_edge', 'ev_100_contracts', 'confidence']
    timestamp = datetime.now().isoformat()

    with open(filepath, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for opp in opportunities:
            writer.writerow({
                'scan_timestamp': timestamp,
                'sport': opp.sport,
                'home_team': opp.home_team,
                'away_team': opp.away_team,
                'kalshi_ticker': opp.kalshi_ticker,
                'recommended_position': opp.recommended_position,
                'net_edge': f"{opp.net_edge:.4f}",
                'ev_100_contracts': f"{opp.expected_value_100_contracts:.2f}",
                'confidence': opp.confidence
            })

    print(f"Appended {len(opportunities)} opportunities to {filepath}")
