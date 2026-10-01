"""Repeatable microbenchmark for TidyID's hot generation path."""

from __future__ import annotations

import json
import os
import platform
import time

from tidyid import tidyid

LENGTHS = (8, 10, 16, 32, 64, 256)
WARMUP_CALLS = 10_000
MEASURED_CALLS = 100_000
SAMPLE_COUNT = 100
SAMPLE_CALLS = MEASURED_CALLS // SAMPLE_COUNT


def measure(length: int, allow_uppercase: bool = False) -> dict[str, int]:
    checksum = 0
    generate = tidyid
    for _ in range(WARMUP_CALLS):
        checksum ^= ord(generate(length, allow_uppercase)[0])

    samples: list[int] = []
    started = time.perf_counter_ns()
    for _ in range(SAMPLE_COUNT):
        sample_started = time.perf_counter_ns()
        for _ in range(SAMPLE_CALLS):
            checksum ^= ord(generate(length, allow_uppercase)[0])
        samples.append(time.perf_counter_ns() - sample_started)
    duration = time.perf_counter_ns() - started
    samples.sort()

    def percentile(value: float) -> int:
        index = max(0, int(len(samples) * value + 0.999999) - 1)
        return round(samples[index] / SAMPLE_CALLS)

    return {
        "ops_per_second": round(MEASURED_CALLS * 1e9 / duration),
        "p50_nanoseconds": percentile(0.50),
        "p95_nanoseconds": percentile(0.95),
        "p99_nanoseconds": percentile(0.99),
        "checksum": checksum,
    }


def main() -> None:
    print(
        json.dumps(
            {
                "runtime": platform.python_version(),
                "implementation": platform.python_implementation(),
                "platform": platform.platform(),
                "cpu_count": os.cpu_count(),
                "warmup_calls": WARMUP_CALLS,
                "measured_calls": MEASURED_CALLS,
            },
            indent=2,
        )
    )
    for length in LENGTHS:
        print(
            json.dumps(
                {
                    "length": length,
                    "default": measure(length),
                    "allow_uppercase": measure(length, True),
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
