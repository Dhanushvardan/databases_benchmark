from pathlib import Path

from benchmark.adapters.tigerGraph import TigerGraphAdapter
from benchmark.workloads.lookup import benchmark_lookup


def read_edges(file_path):
    edges = []

    with Path(file_path).open(
        "r",
        encoding="utf-8"
    ) as file:

        import csv

        reader = csv.DictReader(file)

        for row in reader:
            edges.append(
                (
                    int(row["src"]),
                    int(row["dst"])
                )
            )

    return edges


def main():

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

    if not edges:
        print("Dataset is empty.")
        return

    # ---------------------------------------------------------
    # Lookup nodes
    # ---------------------------------------------------------

    node_ids = []

    for src, dst in edges:

        src = str(src)

        if src not in node_ids:
            node_ids.append(src)

        if len(node_ids) == 10:
            break

    print(
        f"Using {len(node_ids)} lookup nodes."
    )

    print(
        f"Lookup nodes: {node_ids}"
    )

    # ---------------------------------------------------------
    # TigerGraph
    # ---------------------------------------------------------

    print(
        "\nConnecting to TigerGraph..."
    )

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
    # Lookup operation
    # ---------------------------------------------------------

    def lookup_operation(node_id):
        return adapter.get_vertex(
            "node",
            node_id
        )

    # ---------------------------------------------------------
    # Benchmark
    # ---------------------------------------------------------

    print(
        "\nRunning TigerGraph lookup benchmark..."
    )

    try:

        result = benchmark_lookup(
            operation=lookup_operation,
            node_ids=node_ids,
            warmup=20,
            iterations=100
        )

    except Exception as exc:

        print(
            f"\nTigerGraph lookup failed: {exc}"
        )

        adapter.close()
        return

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------

    print(
        "\n=== TigerGraph Lookup Result ==="
    )

    print(
        f"Iterations: "
        f"{result['iterations']}"
    )

    print(
        f"Warmup: "
        f"{result['warmup']}"
    )

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

    adapter.close()


if __name__ == "__main__":
    main()