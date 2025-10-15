#!/usr/bin/env python3
"""
Educational wordlist-based hash cracker supporting SHA-1/SHA-256/MD5 for learning.
- Intended for local lab usage only; small wordlist by default
- Prints the first match and exits

Usage:
  python tools/hash_cracker.py --hash 5d41402abc4b2a76b9719d911017c592 --alg md5 --wordlist wordlists/passwords.txt
"""
from __future__ import annotations
import argparse
import hashlib
from typing import Optional

SUPPORTED = {"md5", "sha1", "sha256"}


def compute_hash(data: str, alg: str) -> str:
    encoded = data.encode('utf-8')
    if alg == 'md5':
        return hashlib.md5(encoded).hexdigest()
    if alg == 'sha1':
        return hashlib.sha1(encoded).hexdigest()
    if alg == 'sha256':
        return hashlib.sha256(encoded).hexdigest()
    raise ValueError("Unsupported algorithm")


def crack(target_hash: str, alg: str, wordlist_path: str) -> Optional[str]:
    target_hash = target_hash.lower()
    with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            candidate = line.strip()
            if not candidate:
                continue
            if compute_hash(candidate, alg) == target_hash:
                return candidate
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description='Educational hash cracker (md5, sha1, sha256)')
    parser.add_argument('--hash', required=True, help='Target hash (hex)')
    parser.add_argument('--alg', default='md5', choices=sorted(SUPPORTED), help='Hash algorithm (default: md5)')
    parser.add_argument('--wordlist', default='wordlists/passwords.txt', help='Wordlist path')
    args = parser.parse_args()

    result = crack(args.hash, args.alg, args.wordlist)
    if result is None:
        print('No match found')
    else:
        print(f'Match: {result}')


if __name__ == '__main__':
    main()
