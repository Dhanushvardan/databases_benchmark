import json
from pathlib import Path

from benchmark.adapters.cognodb import CognoDBAdapter
from benchmark.workloads.footprint import (
    benchmark_footprint
)


def main():

    db = CognoDBAdapter()

    try:

        db.connect()

        result = benchmark_footprint(
            db
        )

        output = {
            "database": "CognoDB",
            **result
        }

        print()
        print("=== CognoDB Footprint Result ===")

        print(
            f"Nodes: "
            f"{result['dataset']['nodes']}"
        )

        print(
            f"Relationships: "
            f"{result['dataset']['relationships']}"
        )

        print(
            f"Client memory: "
            f"{result['client']['client_memory_mb']} MB"
        )

        print(
            f"Platform: "
            f"{result['client']['platform']}"
        )

        print(
            f"Python: "
            f"{result['client']['python_version']}"
        )

        print(
            f"CPU count: "
            f"{result['client']['cpu_count']}"
        )

        output_dir = Path(
            "results/raw"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file = (
            output_dir /
            "cognodb_footprint.json"
        )

        with output_file.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                output,
                file,
                indent=4
            )

        print()
        print(
            f"Results saved to {output_file}"
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()