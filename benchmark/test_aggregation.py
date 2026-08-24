import json
from pathlib import Path

from benchmark.adapters.cognodb import CognoDBAdapter
from benchmark.workloads.aggregation import (
    benchmark_aggregation
)


def main():

    db = CognoDBAdapter()

    try:

        db.connect()

        print("Running aggregation benchmark...")

        result = benchmark_aggregation(
            db,
            warmup=20,
            iterations=100
        )

        print()
        print("=== Aggregation Result ===")

        print(
            f"p50: "
            f"{result['p50_ms']:.4f} ms"
        )

        print(
            f"p95: "
            f"{result['p95_ms']:.4f} ms"
        )

        print(
            f"Average: "
            f"{result['average_ms']:.4f} ms"
        )

        output = Path(
            "results/raw/cognodb_aggregation.json"
        )

        with output.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4
            )

        print()
        print(
            f"Results saved to {output}"
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()