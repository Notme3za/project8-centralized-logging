#!/usr/bin/env python3
"""Alert on repeated failed SSH password attempts in recent collected logs."""

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

FAILED_PASSWORD = re.compile(
    r"sshd\[\d+\]: Failed password for "
    r"(?:invalid user )?\S+ from (?P<ip>\S+) port \d+"
)


def main():
    parser = argparse.ArgumentParser(
        description="Detect repeated failed SSH passwords by source IP."
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path("/var/log/remote"),
        help="Directory containing one sender folder per host.",
    )
    parser.add_argument("--threshold", type=int, default=5)
    parser.add_argument("--window-minutes", type=int, default=5)
    args = parser.parse_args()

    if args.threshold < 1 or args.window_minutes < 1:
        parser.error("--threshold and --window-minutes must be positive")

    log_files = sorted(args.log_dir.glob("*/auth.log"))
    if not log_files:
        print(f"ERROR: no collected auth.log files found in {args.log_dir}")
        return 2

    now = datetime.now().astimezone()
    window_start = now - timedelta(minutes=args.window_minutes)
    events_by_ip = defaultdict(list)
    matched_events = 0

    for log_file in log_files:
        with log_file.open(encoding="utf-8", errors="replace") as log:
            for line in log:
                match = FAILED_PASSWORD.search(line)
                if not match:
                    continue

                try:
                    event_time = datetime.fromisoformat(line.split(maxsplit=1)[0])
                    if event_time.tzinfo is None:
                        event_time = event_time.astimezone()
                except (ValueError, IndexError):
                    continue

                event_time = event_time.astimezone()
                if window_start <= event_time <= now:
                    events_by_ip[match.group("ip")].append(event_time)
                    matched_events += 1

    alerts = []
    window = timedelta(minutes=args.window_minutes)

    for source_ip, timestamps in events_by_ip.items():
        timestamps.sort()
        left = 0

        for right, event_time in enumerate(timestamps):
            while event_time - timestamps[left] > window:
                left += 1

            count = right - left + 1
            if count >= args.threshold:
                first = timestamps[left].isoformat(timespec="seconds")
                last = event_time.isoformat(timespec="seconds")
                alerts.append((source_ip, count, first, last))
                break

    if alerts:
        for source_ip, count, first, last in sorted(alerts):
            print(
                f"ALERT: {count} failed SSH password attempts from {source_ip} "
                f"within {args.window_minutes} minutes "
                f"({first} to {last})"
            )
        return 1

    print(
        f"No alert: {matched_events} failed SSH password event(s) in the last "
        f"{args.window_minutes} minutes; threshold is {args.threshold} "
        "from one source IP."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
