import json
from pathlib import Path

from benchmark.adapters.cognodb import CognoDBAdapter

from benchmark.workloads.traversal import (
    benchmark_traversal
)


def main():

    db = CognoDBAdapter()

    try:

        db.connect()

        # Make sure the benchmark index exists.
        db.create_indexes()

        # Get a fixed set of starting nodes.
        start_nodes = db.get_start_nodes(
            limit=100
        )

        print(
            f"Using {len(start_nodes)} start nodes."
        )

        results = []

        for hops in [1, 2, 3]:

            print()
            print(
                f"Running {hops}-hop benchmark..."
            )

            result = benchmark_traversal(
                db,
                start_nodes,
                hops,
                warmup=20,
                iterations=100
            )

            results.append(result)

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

        output_dir = Path(
            "results/raw"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file = (
            output_dir /
            "cognodb_traversal.json"
        )

        with output_file.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                results,
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