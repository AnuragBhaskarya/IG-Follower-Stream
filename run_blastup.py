#!/usr/bin/env python3
"""
Instagram Follower Tracker - Blastup API
Requires CSRF token extraction.
"""

from apis.blastup import fetch_follower_count
from core.tracker import run_tracker

if __name__ == "__main__":
    run_tracker(fetch_follower_count, "Blastup API")
