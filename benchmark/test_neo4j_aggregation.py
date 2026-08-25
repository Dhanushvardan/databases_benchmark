import json
from pathlib import Path

from benchmark.adapters.neo4j import Neo4jAdapter
from benchmark.workloads.aggregation import benchmark_aggregation


def main():
    db = Neo4jAdapter()

    try:
        db.connect()

        # Make sure the benchmark index exists.
        db.create_indexes()

        print()
        print("Running aggregation benchmark...")

        result = benchmark_aggregation(
            db,
            warmup=20,
            iterations=100
        )

        print()
        print("=== Neo4j Aggregation Result ===")

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

        print(
            f"Min: "
            f"{result['min_ms']:.4f} ms"
        )

        print(
            f"Max: "
            f"{result['max_ms']:.4f} ms"
        )

        results = {
            "database": "neo4j",
            "query": "degree aggregation by BenchmarkPerson",
            "grouping_property": "BenchmarkPerson.id",
            "relationship_type": "BENCHMARK_KNOWS",
            **result
        }

        output_dir = Path("results/raw")
        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file = output_dir / "neo4j_aggregation.json"

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