"""Console output formatting for value bet opportunities."""

from typing import List
from models.opportunity import ValueOpportunity
from config.settings import SPORT_DISPLAY_NAMES


def get_sport_display_name(sport_key: str) -> str:
    return SPORT_DISPLAY_NAMES.get(sport_key, sport_key.upper())


def format_percentage(value: float, decimals: int = 1) -> str:
    return f"{value * 100:.{decimals}f}%"


def format_dollars(value: float, decimals: int = 2) -> str:
    return f"${value:.{decimals}f}"


def print_header():
    print("\n" + "=" * 80)
    print("VEGAS-KALSHI VALUE BET OPPORTUNITIES")
    print("=" * 80 + "\n")


def print_opportunity(opp: ValueOpportunity, index: int):
    from core.fee_calculator import calculate_kalshi_fee, calculate_effective_cost

    sport_name = get_sport_display_name(opp.sport)

    if opp.recommended_team == 'home':
        bet_team = opp.home_team
        bet_price = opp.kalshi_home_price
        vegas_prob = opp.vegas_home_prob
    else:
        bet_team = opp.away_team
        bet_price = opp.kalshi_away_price
        vegas_prob = opp.vegas_away_prob

    price_cents = int(bet_price * 100)
    min_cost = calculate_effective_cost(bet_price, 1) if 0 < bet_price < 1 else bet_price
    cost_10 = calculate_effective_cost(bet_price, 10) if 0 < bet_price < 1 else bet_price * 10
    cost_50 = calculate_effective_cost(bet_price, 50) if 0 < bet_price < 1 else bet_price * 50
    cost_100 = calculate_effective_cost(bet_price, 100) if 0 < bet_price < 1 else bet_price * 100

    print(f"#{index} | {sport_name}")
    print(f"   Matchup: {opp.away_team} @ {opp.home_team}")
    print()

    print("   " + "+" + "-" * 56 + "+")
    print("   " + "|" + " KALSHI BET ACTION ".center(56) + "|")
    print("   " + "+" + "-" * 56 + "+")
    print("   " + "|" + f"  Ticker: {opp.kalshi_ticker}".ljust(56) + "|")
    print("   " + "|" + f"  Action: BUY YES on {bet_team}".ljust(56) + "|")
    print("   " + "|" + f"  Price:  {price_cents}c per contract".ljust(56) + "|")
    print("   " + "+" + "-" * 56 + "+")
    print()

    print(f"   Edge Analysis:")
    print(f"     Vegas True Prob:  {format_percentage(vegas_prob)}")
    print(f"     Kalshi Price:     {format_percentage(bet_price)} ({price_cents}c)")
    print(f"     Gross Edge:       {format_percentage(opp.gross_edge, 2)}")
    print(f"     Fee/Contract:     {format_dollars(opp.fee_impact, 4)}")
    print(f"     NET EDGE:         {format_percentage(opp.net_edge, 2)}")
    print()

    print(f"   Position Sizing (Kalshi min = 1 contract):")
    print(f"     Contracts    Cost         Profit if Win    EV")
    print(f"     ----------   ----------   --------------   --------")
    print(f"     1 (min)      {format_dollars(min_cost):<10}   {format_dollars(1 - min_cost):<14}   {format_dollars(opp.expected_value_per_contract)}")
    print(f"     10           {format_dollars(cost_10):<10}   {format_dollars(10 - cost_10):<14}   {format_dollars(opp.expected_value_per_contract * 10)}")
    print(f"     50           {format_dollars(cost_50):<10}   {format_dollars(50 - cost_50):<14}   {format_dollars(opp.expected_value_per_contract * 50)}")
    print(f"     100          {format_dollars(cost_100):<10}   {format_dollars(100 - cost_100):<14}   {format_dollars(opp.expected_value_100_contracts)}")
    print()

    print(f"   Confidence: {opp.confidence.upper()} ({opp.num_bookmakers} bookmakers)")
    print("-" * 80)


def print_opportunities(opportunities: List[ValueOpportunity]):
    print_header()
    if not opportunities:
        print("No value opportunities found meeting criteria.\n")
        return
    for i, opp in enumerate(opportunities, 1):
        print_opportunity(opp, i)
        print()


def print_summary(vegas_event_count: int, kalshi_market_count: int,
                  opportunities: List[ValueOpportunity]):
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total Vegas events analyzed: {vegas_event_count}")
    print(f"Kalshi markets checked: {kalshi_market_count}")
    print(f"Value opportunities found: {len(opportunities)}")

    if opportunities:
        avg_edge = sum(o.net_edge for o in opportunities) / len(opportunities)
        print(f"Average net edge: {format_percentage(avg_edge, 2)}")
        total_ev = sum(o.expected_value_100_contracts for o in opportunities)
        print(f"Total EV (100 contracts each): {format_dollars(total_ev)}")

        high_conf = len([o for o in opportunities if o.confidence == 'high'])
        med_conf = len([o for o in opportunities if o.confidence == 'medium'])
        low_conf = len([o for o in opportunities if o.confidence == 'low'])
        print(f"\nBy confidence: High: {high_conf}, Medium: {med_conf}, Low: {low_conf}")

        sports = {}
        for opp in opportunities:
            sport_name = get_sport_display_name(opp.sport)
            sports[sport_name] = sports.get(sport_name, 0) + 1
        print(f"By sport: {', '.join(f'{s}: {c}' for s, c in sorted(sports.items()))}")
    print()


def print_compact_table(opportunities: List[ValueOpportunity]):
    if not opportunities:
        print("No opportunities found.")
        return

    print(f"\n{'Sport':<7} {'BUY YES ON':<25} {'Ticker':<30} {'Price':<7} {'Edge':<8} {'EV':<8}")
    print("-" * 95)

    for opp in opportunities:
        sport = get_sport_display_name(opp.sport)[:6]
        bet_team = opp.home_team[:24] if opp.recommended_team == 'home' else opp.away_team[:24]
        bet_price = opp.kalshi_home_price if opp.recommended_team == 'home' else opp.kalshi_away_price
        price_cents = f"{int(bet_price * 100)}c"
        ticker = opp.kalshi_ticker[:29]
        edge = format_percentage(opp.net_edge, 1)
        ev = format_dollars(opp.expected_value_100_contracts)
        print(f"{sport:<7} {bet_team:<25} {ticker:<30} {price_cents:<7} {edge:<8} {ev:<8}")
    print()
