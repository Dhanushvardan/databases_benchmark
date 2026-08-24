import json
from pathlib import Path

from benchmark.adapters.cognodb import CognoDBAdapter
from benchmark.workloads.lookup import benchmark_lookup


def main():

    db = CognoDBAdapter()

    try:

        db.connect()

        # Make sure index exists.
        db.create_indexes()

        node_ids = db.get_start_nodes(
            limit=100
        )

        print(
            f"Using {len(node_ids)} nodes."
        )

        # -------------------------
        # Point lookup
        # -------------------------

        print()
        print("Running point lookup...")

        point_result = benchmark_lookup(
            db.point_lookup,
            node_ids,
            warmup=20,
            iterations=100
        )

        print(
            f"p50: "
            f"{point_result['p50_ms']:.4f} ms"
        )

        print(
            f"p95: "
            f"{point_result['p95_ms']:.4f} ms"
        )

        # -------------------------
        # Indexed lookup
        # -------------------------

        print()
        print("Running indexed lookup...")

        indexed_result = benchmark_lookup(
            db.indexed_lookup,
            node_ids,
            warmup=20,
            iterations=100
        )

        print(
            f"p50: "
            f"{indexed_result['p50_ms']:.4f} ms"
        )

        print(
            f"p95: "
            f"{indexed_result['p95_ms']:.4f} ms"
        )

        # -------------------------
        # Save
        # -------------------------

        results = {
            "database": "CognoDB",
            "point_lookup": point_result,
            "indexed_lookup": indexed_result
        }

        output = Path(
            "results/raw/cognodb_lookup.json"
        )

        with output.open(
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
            f"Results saved to {output}"
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()