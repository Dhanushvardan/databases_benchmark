from benchmark.adapters.arangodb import ArangoDBAdapter
from benchmark.workloads.aggregation import benchmark_aggregation


def main():

    adapter = ArangoDBAdapter()

    try:

        # =====================================================
        # CONNECTION
        # =====================================================

        adapter.connect()

        # =====================================================
        # AGGREGATION BENCHMARK
        # =====================================================

        print()
        print(
            "Running aggregation benchmark..."
        )

        result = benchmark_aggregation(
            adapter,
            warmup=20,
            iterations=100
        )

        # =====================================================
        # RESULTS
        # =====================================================

        print()
        print(
            "=== ArangoDB Aggregation Result ==="
        )

        print(
            f"Aggregation p50: "
            f"{result['p50_ms']:.4f} ms"
        )

        print(
            f"Aggregation p95: "
            f"{result['p95_ms']:.4f} ms"
        )

        print(
            f"Aggregation average: "
            f"{result['average_ms']:.4f} ms"
        )

        print(
            f"Aggregation min: "
            f"{result['min_ms']:.4f} ms"
        )

        print(
            f"Aggregation max: "
            f"{result['max_ms']:.4f} ms"
        )

    except Exception as e:

        print(
            "ArangoDB aggregation benchmark failed!"
        )

        print(
            "Error:",
            e
        )

    finally:

        adapter.close()


if __name__ == "__main__":
    main()