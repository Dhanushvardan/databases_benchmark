import csv
import time
from pathlib import Path


def read_edges(file_path: str):

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


def benchmark_loading(adapter, edges):

    start = time.perf_counter()

    adapter.load_data(edges)

    elapsed = time.perf_counter() - start

    edge_count = len(edges)

    throughput = edge_count / elapsed

    return {
        "edges": edge_count,
        "load_time_seconds": elapsed,
        "edges_per_second": throughput
    }