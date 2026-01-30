"""
Blastup API - Requires CSRF token extraction.
"""

from typing import Optional
from curl_cffi import requests
import re

from core.config import INSTAGRAM_USERNAME
from core.logger import logger

BLASTUP_URL = "https://blastup.com/instagram-follower-count"

# Global state
_session = None
_token = None

def get_session():
    # impersonate="chrome" handles all the headers and TLS signature for us!
    s = requests.Session(impersonate="chrome")
    s.headers.update({
        "Referer": "https://blastup.com/instagram-follower-count",
        "Origin": "https://blastup.com",
    })
    return s

def get_csrf_token(s: requests.Session) -> Optional[str]:
    """Fetches the CSRF token from the blastup page."""
    try:
        response = s.get(f"{BLASTUP_URL}?{INSTAGRAM_USERNAME}", timeout=30)
        response.raise_for_status()
        
        # Extract token from window.__config.token
        match = re.search(r'token:\s*"([^"]+)"', response.text)
        if match:
            token = match.group(1)
            logger.info(f"Got CSRF Token: {token[:10]}...")
            return token
        
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
    global _session, _token
    
    # Initialize session/token if needed
    if _session is None or _token is None:
        _session = get_session()
        _token = get_csrf_token(_session)
        if not _token:
            return None
            
    try:
        # Add token to headers
        headers = _session.headers.copy()
        headers["X-CSRF-TOKEN"] = _token
        headers["X-Requested-With"] = "XMLHttpRequest"

        response = _session.post(
            BLASTUP_URL,
            json={
                "_token": _token,
                "username": INSTAGRAM_USERNAME
            },
            headers=headers,
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
                # If failed, force refresh session next time
                _session = None
                _token = None
        else:
            logger.error(f"API returned status {response.status_code}")
            # If status error (like 419/500), refresh session
            _session = None
            _token = None
            
        return None
    except Exception as e:
        logger.error(f"Error fetching follower count: {e}")
        # On connection error, maybe keep session, or refresh? Refresh is safer.
        _session = None
        _token = None
        return None
