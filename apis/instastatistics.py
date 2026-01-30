"""
InstaStatistics API - Fastest option with 2-second cache refresh.
"""

from typing import Optional
import requests

from core.config import INSTAGRAM_USERNAME
from core.logger import logger

API_URL = f"https://backend.instastatistics.com/api/likee/instagramfull/{INSTAGRAM_USERNAME}"

# Session with required headers
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://instastatistics.com",
    "Referer": "https://instastatistics.com/",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
})


def fetch_follower_count() -> Optional[int]:
    """Fetches follower count from InstaStatistics API."""
    try:
        response = session.get(API_URL, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                user = data.get("user", {})
                followers = user.get("followerCount")
                
                if followers is None:
                    # Fallback to graphql path
                    graphql = data.get("graphql", {}).get("user", {})
                    edge = graphql.get("edge_followed_by", {})
                    followers = edge.get("count")
                
                if isinstance(followers, int):
                    return followers
                    
                logger.warning("Could not find follower count in response")
            else:
                logger.warning("API returned success=false")
        else:
            logger.error(f"API returned status {response.status_code}")
            
        return None
    except Exception as e:
        logger.error(f"Error fetching follower count: {e}")
        return None
