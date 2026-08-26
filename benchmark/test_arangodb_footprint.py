import csv
import time

from benchmark.adapters.arangodb import ArangoDBAdapter


DATASET_PATH = "data\processed\pokec_100k.csv"


def read_edges():

    edges = []

    print("Reading dataset...")

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.reader(file)

        for row in reader:

            if len(row) < 2:
                continue

            src = row[0].strip()
            dst = row[1].strip()

            # Skip header if present
            if src.lower() in ["source", "src", "from"]:
                continue

            if dst.lower() in ["target", "dst", "to"]:
                continue

            edges.append(
                (src, dst)
            )

    print(
        f"Loaded {len(edges)} edges from CSV."
    )

    return edges


def main():

    adapter = ArangoDBAdapter()

    try:

        # =====================================================
        # CONNECT
        # =====================================================

        adapter.connect()

        # =====================================================
        # READ DATASET
        # =====================================================

        edges = read_edges()

        # =====================================================
        # CLEAR OLD DATA
        # =====================================================

        print(
            "Clearing old benchmark data..."
        )

        adapter.clear_benchmark_data()

        # =====================================================
        # CREATE COLLECTIONS / INDEXES
        # =====================================================

        print(
            "Creating collections and indexes..."
        )

        adapter.create_indexes()

        # =====================================================
        # LOAD DATA
        # =====================================================

        print(
            "Loading dataset into ArangoDB..."
        )

        start = time.perf_counter()

        adapter.load_data(
            edges,
            batch_size=10000
        )

        elapsed = (
            time.perf_counter() - start
        )

        print(
            f"Data loading completed in "
            f"{elapsed:.4f} seconds."
        )

        # =====================================================
        # FOOTPRINT
        # =====================================================

        print()
        print(
            "Running ArangoDB footprint measurement..."
        )

        result = adapter.footprint()

        # =====================================================
        # RESULT
        # =====================================================

        print()
        print(
            "=== ArangoDB Footprint Result ==="
        )

        print(
            f"Vertex documents: "
            f"{result['vertex_documents']}"
        )

        print(
            f"Edge documents: "
            f"{result['edge_documents']}"
        )

        print(
            f"Vertex size: "
            f"{result['vertex_size_bytes']} bytes"
        )

        print(
            f"Edge size: "
            f"{result['edge_size_bytes']} bytes"
        )

        print(
            f"Total size: "
            f"{result['total_size_bytes']} bytes"
        )

        print(
            f"Total size: "
            f"{result['total_size_mb']:.2f} MB"
        )

    except Exception as exc:

        print(
            f"Footprint benchmark failed: {exc}"
        )

    finally:

        adapter.close()


if __name__ == "__main__":
    main()