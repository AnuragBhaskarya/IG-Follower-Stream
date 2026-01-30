"""
Lightricks/PopularPays API - Simple single GET request, no CSRF needed.
"""

from typing import Optional
import requests

from core.config import INSTAGRAM_USERNAME
from core.logger import logger

API_URL = "https://social-media-users-data-api-production.lightricks.workers.dev/instagram"

# Session with required headers
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://popularpays.com",
    "Referer": "https://popularpays.com/",
})


def fetch_follower_count() -> Optional[int]:
    """Fetches the follower count using Lightricks API - single GET request!"""
    try:
        response = session.get(
            API_URL,
            params={"username": INSTAGRAM_USERNAME},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            followers = data.get("followersCount")
            if isinstance(followers, int):
                return followers
            logger.warning(f"Unexpected followers value: {followers}")
        else:
            logger.error(f"API returned status {response.status_code}")
            
        return None
    except Exception as e:
        logger.error(f"Error fetching follower count: {e}")
        return None
