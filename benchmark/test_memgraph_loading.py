import json
from pathlib import Path

from benchmark.adapters.memgraph import MemgraphAdapter
from benchmark.workloads.loading import (
    read_edges,
    benchmark_loading
)


def main():

    db = MemgraphAdapter()

    try:
        db.connect()

        # Clear previous benchmark data
        db.clear_benchmark_data()

        # Create benchmark index
        db.create_indexes()

        # Pokec 100K benchmark dataset
        dataset_path = Path(
            "data/processed/pokec_100k.csv"
        )

        print("Reading dataset...")

        edges = read_edges(
            str(dataset_path)
        )

        print(
            f"Loaded {len(edges)} edges from CSV."
        )

        print(
            "Starting Memgraph ingestion..."
        )

        result = benchmark_loading(
            db,
            edges
        )

        result["database"] = "Memgraph"

        print()
        print(
            "=== Memgraph Loading Result ==="
        )

        print(
            f"Edges: {result['edges']}"
        )

        print(
            f"Time: "
            f"{result['load_time_seconds']:.4f} seconds"
        )

        print(
            f"Throughput: "
            f"{result['edges_per_second']:.2f} edges/sec"
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
            "memgraph_loading.json"
        )

        with output_file.open(
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
            f"Result saved to {output_file}"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()