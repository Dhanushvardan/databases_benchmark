import csv
from pathlib import Path

from benchmark.adapters.tigerGraph import TigerGraphAdapter
from benchmark.workloads.traversal import benchmark_traversal


def read_edges(file_path):
    edges = []

    with Path(file_path).open(
        "r",
        encoding="utf-8"
    ) as file:

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

    # =========================================================
    # DATASET
    # =========================================================

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

    # =========================================================
    # START NODES
    # =========================================================

    start_nodes = []

    for src, dst in edges:

        node_id = str(src)

        if node_id not in start_nodes:
            start_nodes.append(node_id)

        if len(start_nodes) == 10:
            break

    print(
        f"Using {len(start_nodes)} traversal nodes."
    )

    print(
        f"Start nodes: {start_nodes}"
    )

    # =========================================================
    # TIGERGRAPH CONNECTION
    # =========================================================

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

    # =========================================================
    # TRAVERSAL BENCHMARK
    # =========================================================

    hops = 3

    print(
        "\nRunning TigerGraph traversal benchmark..."
    )

    print(
        f"Hops: {hops}"
    )

    try:

        result = benchmark_traversal(
            adapter=adapter,
            start_nodes=start_nodes,
            hops=hops,
            warmup=20,
            iterations=100
        )

    except Exception as exc:

        print(
            f"\nTigerGraph traversal failed: {exc}"
        )

        adapter.close()

        return

    # =========================================================
    # RESULTS
    # =========================================================

    print(
        "\n=== TigerGraph Traversal Result ==="
    )

    print(
        f"Hops: {result['hops']}"
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

    # =========================================================
    # CLOSE
    # =========================================================

    adapter.close()


if __name__ == "__main__":
    main()