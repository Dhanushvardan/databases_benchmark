import csv
import time

from benchmark.adapters.arangodb import ArangoDBAdapter


# Change this only if your Pokec CSV is in a different location
DATASET_PATH = "data/processed/pokec_100k.csv"

BATCH_SIZE = 10000


def load_edges_from_csv(file_path):
    edges = []

    with open(
        file_path,
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
            if src.lower() in ("src", "source"):
                continue

            edges.append((src, dst))

    return edges


def main():

    print("Reading dataset...")

    edges = load_edges_from_csv(
        DATASET_PATH
    )

    print(
        f"Loaded {len(edges)} edges from CSV."
    )

    db = ArangoDBAdapter()

    try:
        # -------------------------
        # CONNECT
        # -------------------------

        db.connect()

        # -------------------------
        # CLEAR OLD DATA
        # -------------------------

        db.clear_benchmark_data()

        # -------------------------
        # CREATE COLLECTIONS
        # -------------------------

        db.create_indexes()

        # -------------------------
        # INGESTION
        # -------------------------

        print(
            "Starting ArangoDB ingestion..."
        )

        start_time = time.perf_counter()

        db.load_data(
            edges,
            batch_size=BATCH_SIZE
        )

        end_time = time.perf_counter()

        elapsed = end_time - start_time

        # -------------------------
        # RESULTS
        # -------------------------

        throughput = (
            len(edges) / elapsed
            if elapsed > 0
            else 0
        )

        print()
        print("=== ArangoDB Loading Result ===")
        print(f"Edges: {len(edges)}")
        print(f"Time: {elapsed:.4f} sec")
        print(
            f"Throughput: {throughput:.2f} edges/sec"
        )

    except Exception as e:

        print(
            "ArangoDB ingestion failed!"
        )
        print("Error:", e)

    finally:

        db.close()


if __name__ == "__main__":
    main()