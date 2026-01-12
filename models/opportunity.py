"""Data models for value betting opportunities."""

from dataclasses import dataclass


@dataclass
class ValueOpportunity:
    """Represents a value betting opportunity."""
    sport: str
    vegas_event_id: str
    kalshi_ticker: str
    home_team: str
    away_team: str
    vegas_home_prob: float
    vegas_away_prob: float
    kalshi_home_price: float
    kalshi_away_price: float
    recommended_position: str
    recommended_team: str
    gross_edge: float
    net_edge: float
    fee_impact: float
    expected_value_per_contract: float
    expected_value_100_contracts: float
    num_bookmakers: int
    confidence: str

    @property
    def display_position(self) -> str:
        """Human-readable position recommendation."""
        team = self.home_team if self.recommended_team == 'home' else self.away_team
        return f"{team} {self.recommended_position.upper()}"

    @property
    def display_edge(self) -> str:
        return f"{self.net_edge:.2%}"


@dataclass
class EdgeCalculation:
    """Detailed edge calculation results."""
    position: str
    kalshi_price: float
    vegas_prob: float
    fee_per_contract: float
    effective_cost: float
    gross_edge: float
    net_edge: float
    expected_value_per_contract: float
    total_expected_value: float
    is_value_bet: bool

    @classmethod
    def calculate(cls, kalshi_price: float, vegas_true_prob: float,
                  num_contracts: int = 100, position: str = 'yes',
                  is_maker: bool = False) -> 'EdgeCalculation':
        """Calculate edge for a position."""
        from core.fee_calculator import calculate_kalshi_fee

        fee = calculate_kalshi_fee(kalshi_price, num_contracts, is_maker)
        fee_per_contract = fee / num_contracts

        if position == 'yes':
            effective_cost = kalshi_price + fee_per_contract
            potential_profit = 1.00 - effective_cost
            expected_value = (vegas_true_prob * potential_profit) - ((1 - vegas_true_prob) * effective_cost)
            gross_edge = vegas_true_prob - kalshi_price
            net_edge = vegas_true_prob - effective_cost
            relevant_prob = vegas_true_prob
        else:
            no_price = 1 - kalshi_price
            effective_cost = no_price + fee_per_contract
            potential_profit = 1.00 - effective_cost
            vegas_no_prob = 1 - vegas_true_prob
            expected_value = (vegas_no_prob * potential_profit) - ((1 - vegas_no_prob) * effective_cost)
            gross_edge = vegas_no_prob - no_price
            net_edge = vegas_no_prob - effective_cost
            kalshi_price = no_price
            relevant_prob = vegas_no_prob

        return cls(
            position=position,
            kalshi_price=kalshi_price,
            vegas_prob=relevant_prob,
            fee_per_contract=fee_per_contract,
            effective_cost=effective_cost,
            gross_edge=gross_edge,
            net_edge=net_edge,
            expected_value_per_contract=expected_value,
            total_expected_value=expected_value * num_contracts,
            is_value_bet=net_edge > 0
        )
