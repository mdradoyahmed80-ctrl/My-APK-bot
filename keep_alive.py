"""
Keep-alive pinger for Render (free plan) / any sleeping web service.

Every 9-10 minutes (random) it sends a GET request to your site's /health
endpoint so the service does not go to sleep.

Usage:
    SITE_URL=https://your-service.onrender.com python keep_alive.py

Stop with Ctrl+C.
"""

import os
import random
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime

SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")
HEALTH_PATH = os.environ.get("HEALTH_PATH", "/health")

MIN_INTERVAL = 9 * 60   # 9 minutes
MAX_INTERVAL = 10 * 60  # 10 minutes
TIMEOUT = 30            # seconds to wait for a response


def log(msg: str) -> None:
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def ping() -> None:
    url = SITE_URL + HEALTH_PATH
    req = urllib.request.Request(url, headers={"User-Agent": "keep-alive/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            log(f"OK  {resp.status}  {url}")
    except urllib.error.HTTPError as e:
        # The server answered, so it is awake even if the status is an error.
        log(f"HTTP {e.code}  {url}")
    except Exception as e:  # network error, DNS error, timeout, etc.
        log(f"FAIL  {url}  ->  {e}")


def main() -> None:
    if not SITE_URL:
        print("Error: SITE_URL environment variable is not set.")
        print("Example: SITE_URL=https://your-service.onrender.com python keep_alive.py")
        sys.exit(1)

    log(f"Keep-alive started for {SITE_URL + HEALTH_PATH}")
    ping()  # first ping right away

    while True:
        wait = random.randint(MIN_INTERVAL, MAX_INTERVAL)
        log(f"Next ping in {wait // 60} min {wait % 60} sec")
        try:
            time.sleep(wait)
        except KeyboardInterrupt:
            log("Stopped by user.")
            break
        ping()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Stopped by user.")
