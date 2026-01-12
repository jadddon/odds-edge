# Vegas-Kalshi Value Bet Finder

A tool that compares sports betting odds from Vegas sportsbooks against Kalshi prediction markets to find value betting opportunities.

## What it does

Traditional sportsbooks (DraftKings, FanDuel, etc.) have been pricing sports bets for decades. They employ teams of oddsmakers and use sophisticated models - they're pretty efficient at it.

Kalshi is different. It's a prediction market where prices are driven by individual traders placing bets against each other. There's no central oddsmaker setting the lines. This means Kalshi prices can lag behind Vegas, especially when:
- News breaks (injuries, lineup changes)
- Games are less popular and have fewer traders
- Vegas lines move quickly and Kalshi traders haven't caught up

When Kalshi's price implies a lower probability than Vegas consensus, that's a potential value bet.

This tool:
1. Pulls moneyline odds from multiple Vegas books via [The Odds API](https://the-odds-api.com/)
2. Removes the "vig" (house edge) to get true implied probabilities
3. Compares those probabilities against Kalshi's prices
4. Accounts for Kalshi's fee structure
5. Flags any opportunities where the edge exceeds your threshold (default: 2%)

## Supported Sports

- NFL
- NBA
- NCAAB (Men's College Basketball)
- WNCAAB (Women's College Basketball)
- NHL
- MLB

## Setup

### 1. Clone and install dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Get your API keys

**The Odds API** (required for Vegas odds):
- Sign up at https://the-odds-api.com/
- Free tier gives you 500 requests/month - plenty for casual use

**Kalshi API** (optional):
- The tool works without authentication for public market data
- If you want authenticated access, get your key from Kalshi

### 3. Set up your environment

Create a `.env` file in the project root:

```
ODDS_API_KEY=your_odds_api_key_here
KALSHI_API_KEY=your_kalshi_key_here  # optional
```

## Usage

### Basic run (NFL + NBA)

```bash
python main.py
```

### All supported sports

```bash
python main.py --all-sports
```

### Specific sports

```bash
python main.py --sports basketball_nba icehockey_nhl
```

### Adjust minimum edge threshold

```bash
python main.py --min-edge 0.03  # 3% minimum edge
```

### Dry run (only fetch Kalshi data, no Vegas API calls)

Useful for checking what Kalshi markets are available without using your Odds API quota:

```bash
python main.py --dry-run
```

### Export to CSV

```bash
python main.py --export-csv
```

### Compact output

```bash
python main.py --compact
```

## Example Output

```
#1 | NBA
   Matchup: Milwaukee Bucks @ Denver Nuggets

   +--------------------------------------------------------+
   |                   KALSHI BET ACTION                    |
   +--------------------------------------------------------+
   |  Ticker: KXNBAGAME-26JAN11MILDEN-DEN                   |
   |  Action: BUY YES on Denver Nuggets                     |
   |  Price:  54c per contract                              |
   +--------------------------------------------------------+

   Edge Analysis:
     Vegas True Prob:  62.5%
     Kalshi Price:     54.0% (54c)
     Gross Edge:       8.50%
     Fee/Contract:     $0.0174
     NET EDGE:         6.76%

   Position Sizing (Kalshi min = 1 contract):
     Contracts    Cost         Profit if Win    EV
     ----------   ----------   --------------   --------
     1 (min)      $0.56        $0.44            $0.07
     10           $5.57        $4.43            $0.68
     50           $27.87       $22.13           $3.38
     100          $55.74       $44.26           $6.76

   Confidence: MEDIUM (7 bookmakers)
```

## How the math works

### Removing the vig

Vegas odds include a house edge. If you convert both sides to implied probabilities, they'll add up to more than 100% (usually ~104-105%). We normalize back to 100% to get "true" probabilities.

### Edge calculation

```
Gross Edge = Vegas True Probability - Kalshi Price
Net Edge = Gross Edge - Kalshi Fee Impact
```

### Kalshi fees

Kalshi charges: `ceil(0.07 * contracts * price * (1-price))`

The fee is highest at 50/50 odds and decreases toward the extremes.

## Caveats

- **Markets move fast.** By the time you see an opportunity and place a bet, the price may have changed.
- **Liquidity matters.** Kalshi's sports markets can be thin. You might not get filled at the displayed price.
- **This isn't financial advice.** Sports betting involves risk. Don't bet more than you can afford to lose.
- **API quota.** The Odds API free tier is 500 requests/month. Each sport you query costs 1 request.

## Project Structure

```
odds-edge/
├── api/
│   ├── kalshi_api.py      # Kalshi API client
│   └── odds_api.py        # The Odds API client
├── core/
│   ├── event_matcher.py   # Matches Vegas events to Kalshi markets
│   ├── fee_calculator.py  # Kalshi fee calculations
│   ├── odds_converter.py  # American odds conversion, vig removal
│   └── value_finder.py    # Main analysis logic
├── models/
│   └── opportunity.py     # Data models
├── output/
│   ├── console.py         # Terminal output formatting
│   └── csv_export.py      # CSV export
├── config/
│   └── settings.py        # Configuration
└── main.py                # CLI entry point
```

## License

MIT - do whatever you want with it.
