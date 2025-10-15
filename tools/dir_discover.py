#!/usr/bin/env python3
"""
Educational HTTP directory discovery (wordlist-based) tool.
- Defaults to http://127.0.0.1:8000 and a tiny wordlist
- Respects robots.txt by default unless --ignore-robots is set
- Single-threaded by default to be gentle; can increase workers

Usage:
  python tools/dir_discover.py --url http://127.0.0.1:8000 --wordlist wordlists/paths.txt --status 200,301,302 --workers 20
"""
from __future__ import annotations
import argparse
import concurrent.futures
import urllib.parse
import requests
from typing import List, Set

DEFAULT_STATUSES = {200, 301, 302, 403}
DEFAULT_URL = "http://127.0.0.1:8000"


def load_wordlist(path: str) -> List[str]:
    words: List[str] = []
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            entry = line.strip()
            if not entry or entry.startswith('#'):
                continue
            words.append(entry)
    return words


def fetch_robots(base_url: str) -> Set[str]:
    robots_url = urllib.parse.urljoin(base_url.rstrip('/') + '/', 'robots.txt')
    try:
        resp = requests.get(robots_url, timeout=5)
        if resp.status_code != 200:
            return set()
        disallowed: Set[str] = set()
        for line in resp.text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.lower().startswith('disallow:'):
                path = line.split(':', 1)[1].strip()
                if path:
                    disallowed.add(path.lstrip('/'))
        return disallowed
    except requests.RequestException:
        return set()


def should_skip(path: str, disallowed: Set[str]) -> bool:
    for d in disallowed:
        if path.startswith(d):
            return True
    return False


def try_path(base_url: str, path: str, statuses: Set[int]) -> tuple[str, int | None]:
    url = urllib.parse.urljoin(base_url.rstrip('/') + '/', path)
    try:
        resp = requests.get(url, timeout=5, allow_redirects=False)
        if resp.status_code in statuses:
            return url, resp.status_code
        return url, None
    except requests.RequestException:
        return url, None


def main() -> None:
    parser = argparse.ArgumentParser(description='Educational directory discovery tool')
    parser.add_argument('--url', default=DEFAULT_URL, help='Base URL (default: http://127.0.0.1:8000)')
    parser.add_argument('--wordlist', default='wordlists/paths.txt', help='Wordlist file path')
    parser.add_argument('--status', default='200,301,302,403', help='CSV of status codes to report')
    parser.add_argument('--workers', type=int, default=10, help='Number of concurrent workers')
    parser.add_argument('--ignore-robots', action='store_true', help='Ignore robots.txt rules')
    args = parser.parse_args()

    statuses = {int(s.strip()) for s in args.status.split(',') if s.strip()}

    words = load_wordlist(args.wordlist)

    disallowed: Set[str] = set()
    if not args.ignore_robots:
        disallowed = fetch_robots(args.url)

    results: List[tuple[str, int]] = []

    if args.workers <= 1:
        for w in words:
            if should_skip(w, disallowed):
                continue
            url, code = try_path(args.url, w, statuses)
            if code is not None:
                results.append((url, code))
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for w in words:
                if should_skip(w, disallowed):
                    continue
                futures.append(executor.submit(try_path, args.url, w, statuses))
            for future in concurrent.futures.as_completed(futures):
                url, code = future.result()
                if code is not None:
                    results.append((url, code))

    for url, code in sorted(results):
        print(f"{code} -> {url}")


if __name__ == '__main__':
    main()
