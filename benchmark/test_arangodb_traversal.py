from benchmark.adapters.arangodb import ArangoDBAdapter
from benchmark.workloads.traversal import benchmark_traversal


def main():

    adapter = ArangoDBAdapter()

    try:
        # =========================
        # CONNECTION
        # =========================

        adapter.connect()

        # =========================
        # GET START NODES
        # =========================

        start_nodes = adapter.get_start_nodes(
            limit=100
        )

        print(
            f"Using {len(start_nodes)} start nodes."
        )

        # =========================
        # RUN TRAVERSAL BENCHMARK
        # =========================

        for hops in [1, 2, 3]:

            print()
            print(
                f"Running {hops}-hop traversal benchmark..."
            )

            result = benchmark_traversal(
                adapter,
                start_nodes,
                hops,
                warmup=20,
                iterations=100
            )

            # =========================
            # RESULTS
            # =========================

            print(
                f"{hops}-hop traversal p50: "
                f"{result['p50_ms']:.4f} ms"
            )

            print(
                f"{hops}-hop traversal p95: "
                f"{result['p95_ms']:.4f} ms"
            )

            print(
                f"{hops}-hop traversal average: "
                f"{result['average_ms']:.4f} ms"
            )

            print(
                f"{hops}-hop traversal min: "
                f"{result['min_ms']:.4f} ms"
            )

            print(
                f"{hops}-hop traversal max: "
                f"{result['max_ms']:.4f} ms"
            )

    except Exception as e:

        print(
            "ArangoDB traversal benchmark failed!"
        )

        print("Error:", e)

    finally:

        adapter.close()


if __name__ == "__main__":
    main()