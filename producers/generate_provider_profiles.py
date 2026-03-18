from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from producers.common import produce_record_batches
from producers.scenario_data import provider_profiles


def main() -> None:
    parser = argparse.ArgumentParser(description="Produce provider profile events.")
    parser.add_argument("--limit", type=int, default=0, help="Limit emitted records.")
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--batch-interval-seconds", type=float, default=0.0)
    parser.add_argument("--start-batch", type=int, default=0)
    parser.add_argument("--continuous", action="store_true")
    args = parser.parse_args()

    def record_batches():
        batches = itertools.count(args.start_batch)
        if not args.continuous:
            batches = range(args.start_batch, args.start_batch + args.iterations)
        for batch_number in batches:
            records = provider_profiles(batch_number=batch_number)
            if args.limit > 0:
                records = records[: args.limit]
            yield records

    produce_record_batches(
        topic="providers.profile.raw",
        schema_file="provider_profile_updated.json",
        batches=record_batches(),
        key_field="provider_id",
        sleep_seconds=args.sleep_seconds,
        batch_interval_seconds=args.batch_interval_seconds,
    )


if __name__ == "__main__":
    main()
