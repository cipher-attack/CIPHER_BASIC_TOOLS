#!/usr/bin/env python3
"""
Educational JWT inspector:
- Decodes header and payload without verifying signature by default
- Can verify HS256 signatures with a provided secret

Usage:
  python tools/jwt_inspector.py --token <jwt> [--secret mysecret]
"""
from __future__ import annotations
import argparse
import base64
import hmac
import hashlib
import json
from typing import Tuple, Optional


def b64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def parse_jwt(token: str) -> Tuple[dict, dict, Optional[str]]:
    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError('Invalid JWT format')
    header_b, payload_b, signature_b64 = parts
    header = json.loads(b64url_decode(header_b))
    payload = json.loads(b64url_decode(payload_b))
    return header, payload, signature_b64


def verify_hs256(token: str, secret: str) -> bool:
    header_b, payload_b, signature_b64 = token.split('.')
    signing_input = f"{header_b}.{payload_b}".encode('utf-8')
    expected = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
    expected_b64 = base64.urlsafe_b64encode(expected).decode('utf-8').rstrip('=')
    return hmac.compare_digest(signature_b64, expected_b64)


def main() -> None:
    parser = argparse.ArgumentParser(description='Educational JWT inspector')
    parser.add_argument('--token', required=True, help='JWT token string')
    parser.add_argument('--secret', help='HS256 secret to verify signature')
    args = parser.parse_args()

    header, payload, signature = parse_jwt(args.token)

    print('Header:')
    print(json.dumps(header, indent=2, sort_keys=True))
    print('Payload:')
    print(json.dumps(payload, indent=2, sort_keys=True))
    print('Signature present:' if signature else 'No signature part')

    alg = header.get('alg')
    if args.secret and alg == 'HS256':
        is_valid = verify_hs256(args.token, args.secret)
        print(f'HS256 signature valid: {is_valid}')
    elif args.secret:
        print('Secret provided but only HS256 verification is supported in this tool')


if __name__ == '__main__':
    main()
