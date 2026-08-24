import json
from pathlib import Path

from benchmark.adapters.neo4j import Neo4jAdapter
from benchmark.workloads.loading import (
    read_edges,
    benchmark_loading
)


DATASET = "data/processed/pokec_100k.csv"


def main():

    db = Neo4jAdapter()

    try:

        db.connect()

        # Remove any previous benchmark data.
        db.clear_benchmark_data()

        print("Reading dataset...")

        edges = read_edges(DATASET)

        print(
            f"Loaded {len(edges)} edges from CSV."
        )

        print(
            "Starting Neo4j ingestion..."
        )

        result = benchmark_loading(
            db,
            edges
        )

        result["database"] = "Neo4j"
        result["dataset"] = "Pokec"

        print()
        print(
            "=== Neo4j Loading Result ==="
        )

        print(
            f"Edges: "
            f"{result['edges']}"
        )

        print(
            f"Time: "
            f"{result['load_time_seconds']:.4f} seconds"
        )

        print(
            f"Throughput: "
            f"{result['edges_per_second']:.2f} edges/sec"
        )

        output = Path(
            "results/raw/neo4j_loading.json"
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True
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
            f"Result saved to {output}"
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()