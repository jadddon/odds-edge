"""Configuration settings for Vegas-Kalshi Arbitrage Tool."""

import os
from pathlib import Path

# Load .env file if available
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

# API Keys
ODDS_API_KEY = os.environ.get('ODDS_API_KEY', '')
KALSHI_API_KEY = os.environ.get('KALSHI_API_KEY', '')

# API URLs
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
KALSHI_API_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

# Analysis Parameters
MIN_NET_EDGE = 0.02
MIN_BOOKMAKERS = 3

# Target Sports
TARGET_SPORTS = [
    'americanfootball_nfl', 'basketball_nba', 'basketball_ncaab',
    'basketball_wncaab', 'icehockey_nhl', 'baseball_mlb',
]

SPORT_DISPLAY_NAMES = {
    'americanfootball_nfl': 'NFL', 'basketball_nba': 'NBA',
    'basketball_ncaab': 'NCAAB', 'basketball_wncaab': 'WNCAAB',
    'icehockey_nhl': 'NHL', 'baseball_mlb': 'MLB',
}

# Kalshi Fee Parameters
KALSHI_TAKER_FEE_MULTIPLIER = 0.07
KALSHI_MAKER_FEE_MULTIPLIER = 0.0175

# Output/Request Settings
EXPORT_PATH = './output/'
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1
