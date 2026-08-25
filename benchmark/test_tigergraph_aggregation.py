from benchmark.adapters.tigerGraph import TigerGraphAdapter
from benchmark.workloads.aggregation import benchmark_aggregation


def main():

    # ---------------------------------------------------------
    # TigerGraph connection
    # ---------------------------------------------------------

    print("Connecting to TigerGraph...")

    adapter = TigerGraphAdapter()

    if not adapter.test_connection():
        print("TigerGraph connection failed.")
        return

    print("TigerGraph connection successful!")

    # ---------------------------------------------------------
    # Aggregation benchmark
    # ---------------------------------------------------------

    print(
        "\nRunning TigerGraph aggregation benchmark..."
    )

    try:

        result = benchmark_aggregation(
            adapter=adapter,
            warmup=20,
            iterations=100
        )

    except Exception as exc:

        print(
            f"\nTigerGraph aggregation failed: {exc}"
        )

        adapter.close()
        return

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------

    print(
        "\n=== TigerGraph Aggregation Result ==="
    )

    print(
        f"Iterations: {result['iterations']}"
    )

    print(
        f"Warmup: {result['warmup']}"
    )

    print(
        f"p50: {result['p50_ms']:.4f} ms"
    )

    print(
        f"p95: {result['p95_ms']:.4f} ms"
    )

    print(
        f"Average: {result['average_ms']:.4f} ms"
    )

    print(
        f"Min: {result['min_ms']:.4f} ms"
    )

    print(
        f"Max: {result['max_ms']:.4f} ms"
    )

    # ---------------------------------------------------------
    # Close connection
    # ---------------------------------------------------------

    adapter.close()


if __name__ == "__main__":
    main()