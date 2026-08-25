from pathlib import Path

from benchmark.adapters.tigerGraph import TigerGraphAdapter
from benchmark.workloads.loading import (
    read_edges,
    benchmark_loading,
)


def main():

    # ---------------------------------------------------------
    # Read dataset
    # ---------------------------------------------------------

    dataset_path = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
    / "pokec_100k.csv"
)

    print("Reading dataset...")

    edges = read_edges(
        str(dataset_path)
    )

    print(
        f"Loaded {len(edges)} edges from CSV."
    )

    # ---------------------------------------------------------
    # Connect
    # ---------------------------------------------------------

    print("\nConnecting to TigerGraph...")

    adapter = TigerGraphAdapter()

    if not adapter.test_connection():
        print(
            "TigerGraph connection failed."
        )
        return

    print(
        "TigerGraph connection successful!"
    )

    # ---------------------------------------------------------
    # Benchmark
    # ---------------------------------------------------------

    print(
        "\nStarting TigerGraph ingestion..."
    )

    result = benchmark_loading(
        adapter,
        edges
    )

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------

    print(
        "\n=== TigerGraph Loading Result ==="
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

    adapter.close()


if __name__ == "__main__":
    main()