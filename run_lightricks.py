#!/usr/bin/env python3
"""
Instagram Follower Tracker - Lightricks API
Simple single GET request, no CSRF needed.
"""

from apis.lightricks import fetch_follower_count
from core.tracker import run_tracker

if __name__ == "__main__":
    run_tracker(fetch_follower_count, "Lightricks API")
