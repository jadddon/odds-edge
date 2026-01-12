"""
Odds conversion and vig removal.

Vegas odds include "vig" (vigorish) - the house edge baked into the lines.
If you add up the implied probabilities from Vegas odds, they'll total
more than 100% (usually around 104-105%). That extra percentage is how
sportsbooks make money.

To find the "true" probability, we normalize back to 100%.
This gives us a baseline to compare against Kalshi's prices.
"""

from typing import Tuple


def american_to_implied_prob(american_odds: int) -> float:
    """
    Convert American odds to implied probability.

    American odds are weird:
    - Positive (+150): Underdog. Bet $100 to win $150.
    - Negative (-200): Favorite. Bet $200 to win $100.

    The formula flips based on the sign, which is annoying but whatever.
    """
    if american_odds > 0:
        return 100 / (american_odds + 100)
    return abs(american_odds) / (abs(american_odds) + 100)


def remove_vig(prob_a: float, prob_b: float) -> Tuple[float, float]:
    """
    Remove the vig by normalizing probabilities to 100%.

    Example: If Vegas says Team A is 52% and Team B is 52.5%, that's 104.5% total.
    The vig is 4.5%. We scale both down proportionally to get true odds.
    """
    total = prob_a + prob_b
    if total <= 0:
        raise ValueError("Sum of probabilities must be positive")
    return (prob_a / total, prob_b / total)
