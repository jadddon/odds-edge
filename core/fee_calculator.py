"""
Kalshi fee calculation.

Kalshi charges fees on trades using a formula that's highest at 50/50 odds
and drops toward the extremes. This makes sense - there's more "action"
(and thus more profit for them) on uncertain outcomes.

Formula: ceil(multiplier * contracts * price * (1 - price))
- Taker fee: 7% multiplier (you're taking liquidity)
- Maker fee: 1.75% multiplier (you're providing liquidity)
"""

import math
from config.settings import KALSHI_TAKER_FEE_MULTIPLIER, KALSHI_MAKER_FEE_MULTIPLIER


def calculate_kalshi_fee(price: float, num_contracts: int, is_maker: bool = False) -> float:
    """
    Calculate the fee for a Kalshi trade.

    The fee is rounded UP to the nearest cent (they're not giving you any breaks).
    At 50c, you're paying max fees. At 10c or 90c, fees are much lower.
    """
    if price <= 0 or price >= 1:
        raise ValueError(f"Price must be between 0 and 1 exclusive, got {price}")
    if num_contracts <= 0:
        raise ValueError(f"Number of contracts must be positive, got {num_contracts}")

    multiplier = KALSHI_MAKER_FEE_MULTIPLIER if is_maker else KALSHI_TAKER_FEE_MULTIPLIER
    raw_fee = multiplier * num_contracts * price * (1 - price)

    # Kalshi rounds up - of course they do
    return math.ceil(raw_fee * 100) / 100


def calculate_effective_cost(price: float, num_contracts: int, is_maker: bool = False) -> float:
    """Total cost = price * contracts + fees. This is what actually leaves your account."""
    fee = calculate_kalshi_fee(price, num_contracts, is_maker)
    return (price * num_contracts) + fee
