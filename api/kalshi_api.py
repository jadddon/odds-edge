"""Kalshi API client for fetching sports prediction markets."""

import requests
import time
import logging
from typing import Optional, List, Dict

from config.settings import (
    KALSHI_API_BASE_URL,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_BASE_DELAY
)

logger = logging.getLogger(__name__)


class KalshiClient:
    """Client for interacting with the Kalshi API."""

    BASE_URL = KALSHI_API_BASE_URL

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Kalshi client."""
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers['Content-Type'] = 'application/json'
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                 data: Optional[Dict] = None) -> Dict:
        """Make HTTP request with retry logic."""
        url = f"{self.BASE_URL}{endpoint}"

        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    timeout=REQUEST_TIMEOUT
                )
                response.raise_for_status()
                return response.json()

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(f"Rate limited, waiting {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"HTTP error: {e}")
                    raise

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(RETRY_BASE_DELAY)

        return {}

    def get_markets(self, status: str = 'open', limit: int = 1000,
                    cursor: Optional[str] = None,
                    series_ticker: Optional[str] = None) -> Dict:
        """Fetch markets from Kalshi."""
        params = {'status': status, 'limit': limit}
        if cursor:
            params['cursor'] = cursor
        if series_ticker:
            params['series_ticker'] = series_ticker
        return self._request('GET', '/markets', params=params)

    def get_game_winner_markets(self, sports: List[str] = None,
                                 verbose: bool = False) -> List[Dict]:
        """Get game winner (moneyline) markets for specified sports."""
        if sports is None:
            sports = ['nfl', 'nba']

        series_map = {
            'nfl': 'KXNFLGAME',
            'nba': 'KXNBAGAME',
            'mlb': 'KXMLBGAME',
            'nhl': 'KXNHLGAME',
            'ncaab': 'KXNCAAMBGAME',
            'ncaaw': 'KXNCAAWBGAME',
        }

        all_markets = []

        for sport in sports:
            series = series_map.get(sport.lower())
            if not series:
                continue

            if verbose:
                print(f"  Fetching {sport.upper()} game winner markets...", flush=True)

            try:
                result = self.get_markets(series_ticker=series, limit=200)
                markets = result.get('markets', [])

                for market in markets:
                    ticker = market.get('ticker', '')
                    parts = ticker.split('-')
                    if len(parts) >= 3:
                        market['_team_code'] = parts[-1]
                        market['_game_id'] = parts[1] if len(parts) > 1 else ''
                        market['_sport'] = sport.lower()
                    all_markets.append(market)

                if verbose:
                    print(f"    Found {len(markets)} markets", flush=True)

            except Exception as e:
                if verbose:
                    print(f"    Error fetching {sport}: {e}", flush=True)

        return all_markets
