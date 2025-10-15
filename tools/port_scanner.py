#!/usr/bin/env python3
"""
Educational TCP port scanner.
- Safe-by-default: targets default to localhost only
- Scans a small, common port set unless --ports provided
- Prints timing and open ports

Usage:
  python tools/port_scanner.py --host 127.0.0.1 --ports 22,80,443,8000-8100 --timeout 0.5 --workers 200
"""
from __future__ import annotations
import argparse
import socket
import concurrent.futures
import time
from typing import List, Tuple

DEFAULT_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 5432, 6379, 8000, 8080]


def parse_ports(ports_str: str | None) -> List[int]:
    if not ports_str:
        return DEFAULT_PORTS
    ports: List[int] = []
    for part in ports_str.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            start_s, end_s = part.split('-', 1)
            start, end = int(start_s), int(end_s)
            if start > end:
                start, end = end, start
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))
    return sorted(set([p for p in ports if 1 <= p <= 65535]))


def check_port(host: str, port: int, timeout: float) -> Tuple[int, bool]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            result = sock.connect_ex((host, port))
            return port, result == 0
        except socket.error:
            return port, False


def scan_ports(host: str, ports: List[int], timeout: float, workers: int) -> List[int]:
    open_ports: List[int] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(check_port, host, port, timeout) for port in ports]
        for future in concurrent.futures.as_completed(futures):
            port, is_open = future.result()
            if is_open:
                open_ports.append(port)
    return sorted(open_ports)


def main() -> None:
    parser = argparse.ArgumentParser(description="Educational TCP port scanner (localhost by default)")
    parser.add_argument('--host', default='127.0.0.1', help='Target host (default: 127.0.0.1)')
    parser.add_argument('--ports', default=None, help='Comma-separated ports and ranges, e.g., 22,80,8000-8100')
    parser.add_argument('--timeout', type=float, default=0.3, help='Socket timeout seconds (default: 0.3)')
    parser.add_argument('--workers', type=int, default=200, help='Concurrent workers (default: 200)')
    args = parser.parse_args()

    ports = parse_ports(args.ports)

    start = time.time()
    open_ports = scan_ports(args.host, ports, args.timeout, args.workers)
    elapsed = time.time() - start

    print(f"Scanned {len(ports)} ports on {args.host} in {elapsed:.2f}s")
    if open_ports:
        print("Open ports:", ', '.join(map(str, open_ports)))
    else:
        print("No open ports found")


if __name__ == '__main__':
    main()
