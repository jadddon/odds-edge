"""The Odds API client for fetching Vegas sportsbook odds."""

import requests
import time
import logging
from typing import Optional, List, Dict

from config.settings import (
    ODDS_API_BASE_URL,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_BASE_DELAY
)

logger = logging.getLogger(__name__)


class OddsAPIClient:
    """Client for interacting with The Odds API."""

    BASE_URL = ODDS_API_BASE_URL

    def __init__(self, api_key: str):
        """Initialize Odds API client."""
        if not api_key:
            raise ValueError("API key is required for The Odds API")
        self.api_key = api_key
        self.session = requests.Session()
        self.remaining_requests = None
        self.used_requests = None

    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make HTTP GET request with retry logic."""
        url = f"{self.BASE_URL}{endpoint}"
        params = params or {}
        params['apiKey'] = self.api_key

        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url=url, params=params, timeout=REQUEST_TIMEOUT)
                self.remaining_requests = response.headers.get('x-requests-remaining')
                self.used_requests = response.headers.get('x-requests-used')
                response.raise_for_status()
                return response.json()

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(f"Rate limited, waiting {delay}s...")
                    time.sleep(delay)
                elif e.response.status_code == 401:
                    raise ValueError("Invalid API key")
                else:
                    logger.error(f"HTTP error: {e}")
                    raise

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(RETRY_BASE_DELAY)

        return []

    def get_quota_info(self) -> Dict:
        """Get current API quota information."""
        return {'remaining': self.remaining_requests, 'used': self.used_requests}

    def get_h2h_odds(self, sport: str, regions: str = 'us') -> List[Dict]:
        """Get head-to-head (moneyline) odds for a sport."""
        params = {'regions': regions, 'markets': 'h2h', 'oddsFormat': 'american'}
        result = self._request(f'/sports/{sport}/odds', params=params)
        if self.remaining_requests:
            logger.info(f"API quota remaining: {self.remaining_requests}")
        return result
