#!/usr/bin/env python3
"""
Instagram Follower Tracker - InstaStatistics API
Fastest option with 2-second cache refresh!
"""

from apis.instastatistics import fetch_follower_count
from core.tracker import run_tracker

if __name__ == "__main__":
    run_tracker(fetch_follower_count, "InstaStatistics API - 2s cache")
