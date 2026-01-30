"""
Blastup API - Requires CSRF token extraction.
"""

from typing import Optional
import requests
import re

from core.config import INSTAGRAM_USERNAME
from core.logger import logger

BLASTUP_URL = "https://blastup.com/instagram-follower-count"

# Session for persistent cookies
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
})


def get_csrf_token() -> Optional[str]:
    """Fetches the CSRF token from the blastup page."""
    try:
        response = session.get(f"{BLASTUP_URL}?{INSTAGRAM_USERNAME}", timeout=30)
        response.raise_for_status()
        
        # Extract token from window.__config.token
        match = re.search(r'token:\s*"([^"]+)"', response.text)
        if match:
            return match.group(1)
        
        # Try meta tag as fallback
        match = re.search(r'<meta name="csrf-token" content="([^"]+)"', response.text)
        if match:
            return match.group(1)
            
        logger.error("Could not find CSRF token in page")
        return None
    except Exception as e:
        logger.error(f"Error fetching CSRF token: {e}")
        return None


def fetch_follower_count() -> Optional[int]:
    """Fetches the follower count using the Blastup API."""
    try:
        token = get_csrf_token()
        if not token:
            return None
        
        response = session.post(
            BLASTUP_URL,
            json={
                "_token": token,
                "username": INSTAGRAM_USERNAME
            },
            headers={
                "Content-Type": "application/json",
                "Origin": "https://blastup.com",
                "Referer": f"{BLASTUP_URL}?{INSTAGRAM_USERNAME}",
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                followers = data.get("followers")
                if isinstance(followers, int):
                    return followers
                logger.warning(f"Unexpected followers value: {followers}")
            else:
                logger.warning(f"API returned success=false: {data}")
        else:
            logger.error(f"API returned status {response.status_code}")
            
        return None
    except Exception as e:
        logger.error(f"Error fetching follower count: {e}")
        return None
