from benchmark.adapters.tigerGraph import TigerGraphAdapter
from benchmark.workloads.footprint import benchmark_footprint


def main():

    print("Connecting to TigerGraph...")

    adapter = TigerGraphAdapter()

    if not adapter.test_connection():
        print("TigerGraph connection failed.")
        return

    print("TigerGraph connection successful!")

    print("\nRunning TigerGraph footprint benchmark...")

    try:
        result = benchmark_footprint(adapter)

    except Exception as exc:
        print(
            f"\nTigerGraph footprint failed: {exc}"
        )
        adapter.close()
        return

    print(
        "\n=== TigerGraph Footprint Result ==="
    )

    print(
        f"Nodes: {result['nodes']}"
    )

    print(
        f"Relationships: "
        f"{result['relationships']}"
    )

    print(
        f"Client Memory: "
        f"{result['client_memory_mb']:.2f} MB"
    )

    print(
        f"Platform: "
        f"{result['platform']}"
    )

    print(
        f"Python Version: "
        f"{result['python_version']}"
    )

    print(
        f"CPU Count: "
        f"{result['cpu_count']}"
    )

    adapter.close()


if __name__ == "__main__":
    main()