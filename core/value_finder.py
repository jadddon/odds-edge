"""
Value bet identification.

This is where the magic happens. We compare Vegas consensus odds (with vig removed)
against Kalshi's prediction market prices. When Vegas thinks a team has a higher
win probability than Kalshi's price implies, that's a potential value bet.

But we have to account for Kalshi's fees too - a small edge gets eaten by fees.
We only flag opportunities with meaningful edge after fees (default: 2%+).
"""

import statistics
import logging
from typing import List, Dict, Optional

from core.odds_converter import american_to_implied_prob, remove_vig
from core.event_matcher import EventMatcher
from models.opportunity import ValueOpportunity, EdgeCalculation
from config.settings import MIN_NET_EDGE, MIN_BOOKMAKERS

logger = logging.getLogger(__name__)


class ValueFinder:
    """Finds value betting opportunities by comparing Vegas odds to Kalshi prices."""

    def __init__(self, min_edge: float = MIN_NET_EDGE, min_bookmakers: int = MIN_BOOKMAKERS):
        self.min_edge = min_edge
        self.min_bookmakers = min_bookmakers
        self.matcher = EventMatcher()

    def _process_vegas_event(self, event: Dict) -> Optional[Dict]:
        """
        Build consensus probability from multiple bookmakers.

        We use the median (not mean) because it's more robust to outliers.
        One weird line from a sketchy book won't throw off our numbers.
        """
        bookmakers = event.get('bookmakers', [])
        if len(bookmakers) < self.min_bookmakers:
            return None  # Not enough data to trust

        home_probs, away_probs = [], []
        home_team = event.get('home_team', '')
        away_team = event.get('away_team', '')

        for book in bookmakers:
            for market in book.get('markets', []):
                if market['key'] != 'h2h':
                    continue
                outcomes = {o['name']: o['price'] for o in market['outcomes']}
                if home_team in outcomes and away_team in outcomes:
                    # Convert American odds to probability, then remove the vig
                    home_impl = american_to_implied_prob(outcomes[home_team])
                    away_impl = american_to_implied_prob(outcomes[away_team])
                    home_true, away_true = remove_vig(home_impl, away_impl)
                    home_probs.append(home_true)
                    away_probs.append(away_true)

        if not home_probs:
            return None

        return {
            'home_prob': statistics.median(home_probs),
            'away_prob': statistics.median(away_probs),
            'num_bookmakers': len(home_probs),
            'home_std': statistics.stdev(home_probs) if len(home_probs) > 1 else 0,
            'away_std': statistics.stdev(away_probs) if len(away_probs) > 1 else 0
        }

    def _determine_confidence(self, num_bookmakers: int, prob_std: float) -> str:
        """
        How confident are we in this opportunity?

        More bookmakers + low variance = high confidence.
        Fewer bookmakers or books disagreeing = lower confidence.
        """
        if num_bookmakers >= 8 and prob_std < 0.02:
            return 'high'
        elif num_bookmakers >= 5 and prob_std < 0.04:
            return 'medium'
        return 'low'

    def find_game_winner_value(self, vegas_events: List[Dict],
                                kalshi_markets: List[Dict],
                                verbose: bool = False) -> List[ValueOpportunity]:
        """
        Find value bets in game winner (moneyline) markets.

        This matches Vegas events to Kalshi markets, compares probabilities,
        and returns any opportunities where the edge exceeds our threshold.
        """
        opportunities = []
        matches = self.matcher.match_game_winner_markets(vegas_events, kalshi_markets)

        if verbose:
            print(f"  Matched {len(matches)} games between Vegas and Kalshi", flush=True)

        for match in matches:
            vegas_event = match['vegas_event']
            home_market = match.get('kalshi_home_market')
            away_market = match.get('kalshi_away_market')

            vegas_probs = self._process_vegas_event(vegas_event)
            if not vegas_probs:
                continue

            # Check home team for value
            if home_market:
                home_price = home_market.get('yes_ask', 0) / 100
                if 0 < home_price < 1:
                    home_calc = EdgeCalculation.calculate(
                        kalshi_price=home_price,
                        vegas_true_prob=vegas_probs['home_prob'],
                        num_contracts=100,
                        position='yes'
                    )
                    if home_calc.net_edge >= self.min_edge:
                        prob_std = max(vegas_probs.get('home_std', 0), vegas_probs.get('away_std', 0))
                        opp = ValueOpportunity(
                            sport=vegas_event.get('sport_key', 'unknown'),
                            vegas_event_id=vegas_event.get('id', ''),
                            kalshi_ticker=home_market.get('ticker', ''),
                            home_team=vegas_event.get('home_team', ''),
                            away_team=vegas_event.get('away_team', ''),
                            vegas_home_prob=vegas_probs['home_prob'],
                            vegas_away_prob=vegas_probs['away_prob'],
                            kalshi_home_price=home_price,
                            kalshi_away_price=away_market.get('yes_ask', 0) / 100 if away_market else 0,
                            recommended_position='yes',
                            recommended_team='home',
                            gross_edge=home_calc.gross_edge,
                            net_edge=home_calc.net_edge,
                            fee_impact=home_calc.fee_per_contract,
                            expected_value_per_contract=home_calc.expected_value_per_contract,
                            expected_value_100_contracts=home_calc.total_expected_value,
                            num_bookmakers=vegas_probs['num_bookmakers'],
                            confidence=self._determine_confidence(vegas_probs['num_bookmakers'], prob_std)
                        )
                        opportunities.append(opp)
                        if verbose:
                            print(f"    Value: {vegas_event.get('home_team')} YES @ {home_price:.0%} "
                                  f"(Vegas: {vegas_probs['home_prob']:.0%}) = {home_calc.net_edge:.1%} edge", flush=True)

            # Check away team for value
            if away_market:
                away_price = away_market.get('yes_ask', 0) / 100
                if 0 < away_price < 1:
                    away_calc = EdgeCalculation.calculate(
                        kalshi_price=away_price,
                        vegas_true_prob=vegas_probs['away_prob'],
                        num_contracts=100,
                        position='yes'
                    )
                    if away_calc.net_edge >= self.min_edge:
                        prob_std = max(vegas_probs.get('home_std', 0), vegas_probs.get('away_std', 0))
                        opp = ValueOpportunity(
                            sport=vegas_event.get('sport_key', 'unknown'),
                            vegas_event_id=vegas_event.get('id', ''),
                            kalshi_ticker=away_market.get('ticker', ''),
                            home_team=vegas_event.get('home_team', ''),
                            away_team=vegas_event.get('away_team', ''),
                            vegas_home_prob=vegas_probs['home_prob'],
                            vegas_away_prob=vegas_probs['away_prob'],
                            kalshi_home_price=home_market.get('yes_ask', 0) / 100 if home_market else 0,
                            kalshi_away_price=away_price,
                            recommended_position='yes',
                            recommended_team='away',
                            gross_edge=away_calc.gross_edge,
                            net_edge=away_calc.net_edge,
                            fee_impact=away_calc.fee_per_contract,
                            expected_value_per_contract=away_calc.expected_value_per_contract,
                            expected_value_100_contracts=away_calc.total_expected_value,
                            num_bookmakers=vegas_probs['num_bookmakers'],
                            confidence=self._determine_confidence(vegas_probs['num_bookmakers'], prob_std)
                        )
                        opportunities.append(opp)
                        if verbose:
                            print(f"    Value: {vegas_event.get('away_team')} YES @ {away_price:.0%} "
                                  f"(Vegas: {vegas_probs['away_prob']:.0%}) = {away_calc.net_edge:.1%} edge", flush=True)

        # Best opportunities first
        return sorted(opportunities, key=lambda x: x.net_edge, reverse=True)
