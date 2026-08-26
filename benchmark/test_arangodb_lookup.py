from benchmark.adapters.arangodb import ArangoDBAdapter
from benchmark.workloads.lookup import benchmark_lookup


def main():

    adapter = ArangoDBAdapter()

    try:

        # =====================================================
        # CONNECTION
        # =====================================================

        adapter.connect()

        # =====================================================
        # GET TEST NODE IDS
        # =====================================================

        node_ids = adapter.get_start_nodes(
            limit=100
        )

        print(
            f"Using {len(node_ids)} lookup nodes."
        )

        # =====================================================
        # POINT LOOKUP
        # =====================================================

        print()
        print(
            "Running point lookup benchmark..."
        )

        point_result = benchmark_lookup(
            adapter.point_lookup,
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

        print(
            f"Point lookup min: "
            f"{point_result['min_ms']:.4f} ms"
        )

        print(
            f"Point lookup max: "
            f"{point_result['max_ms']:.4f} ms"
        )

        # =====================================================
        # INDEXED LOOKUP
        # =====================================================

        print()
        print(
            "Running indexed lookup benchmark..."
        )

        indexed_result = benchmark_lookup(
            adapter.indexed_lookup,
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

        print(
            f"Indexed lookup min: "
            f"{indexed_result['min_ms']:.4f} ms"
        )

        print(
            f"Indexed lookup max: "
            f"{indexed_result['max_ms']:.4f} ms"
        )

    except Exception as e:

        print(
            "ArangoDB lookup benchmark failed!"
        )

        print(
            "Error:",
            e
        )

    finally:

        adapter.close()


if __name__ == "__main__":
    main()