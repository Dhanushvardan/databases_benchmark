import json
from pathlib import Path

from benchmark.adapters.neo4j import Neo4jAdapter
from benchmark.workloads.lookup import benchmark_lookup


def main():
    db = Neo4jAdapter()

    try:
        db.connect()

        # Make sure the benchmark index exists.
        db.create_indexes()

        # Get lookup node IDs.
        node_ids = db.get_start_nodes(limit=100)

        print(f"Using {len(node_ids)} lookup nodes.")

        # -------------------------
        # Point lookup
        # -------------------------

        print()
        print("Running point lookup benchmark...")

        point_result = benchmark_lookup(
            db.point_lookup,
            node_ids,
            warmup=20,
            iterations=100
        )

        print(
            f"Point lookup p50: "
            f"{point_result['p50_ms']:.4f} ms"
        )

        print(
            f"Point lookup p95: "
            f"{point_result['p95_ms']:.4f} ms"
        )

        print(
            f"Point lookup average: "
            f"{point_result['average_ms']:.4f} ms"
        )

        # -------------------------
        # Indexed lookup
        # -------------------------

        print()
        print("Running indexed lookup benchmark...")

        indexed_result = benchmark_lookup(
            db.indexed_lookup,
            node_ids,
            warmup=20,
            iterations=100
        )

        print(
            f"Indexed lookup p50: "
            f"{indexed_result['p50_ms']:.4f} ms"
        )

        print(
            f"Indexed lookup p95: "
            f"{indexed_result['p95_ms']:.4f} ms"
        )

        print(
            f"Indexed lookup average: "
            f"{indexed_result['average_ms']:.4f} ms"
        )

        # -------------------------
        # Save results
        # -------------------------

        results = {
            "database": "neo4j",
            "indexed_properties": [
                "BenchmarkPerson.id"
            ],
            "point_lookup": point_result,
            "indexed_lookup": indexed_result
        }

        output_dir = Path("results/raw")
        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file = output_dir / "neo4j_lookup.json"

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
        print(f"Results saved to {output_file}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
    