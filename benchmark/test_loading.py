import json

from benchmark.adapters.cognodb import CognoDBAdapter

from benchmark.workloads.loading import (
    read_edges,
    benchmark_loading
)


DATASET = "data/processed/pokec_100k.csv"


def main():

    db = CognoDBAdapter()

    try:

        db.connect()

        # Remove only our benchmark data.
        db.clear_benchmark_data()

        # Read Pokec dataset.
        print("Reading dataset...")

        edges = read_edges(DATASET)

        print(
            f"Loaded {len(edges)} edges from CSV."
        )

        # Load into CognoDB and measure it.
        print("Starting CognoDB ingestion...")

        result = benchmark_loading(
            db,
            edges
        )

        print()
        print("=== CognoDB Loading Result ===")
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

        # Save result.
        output = (
            "results/raw/cognodb_loading.json"
        )

        with open(
            output,
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