import csv
import statistics
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from benchmark.adapters.tigerGraph import TigerGraphAdapter
from benchmark.workloads.mixed import benchmark_mixed_worker


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


def percentile(values, percentile):

    values = sorted(values)

    index = int(
        (percentile / 100) * len(values)
    )

    index = min(
        index,
        len(values) - 1
    )

    return values[index]


def run_worker(node_ids, operations):

    adapter = TigerGraphAdapter()

    if not adapter.test_connection():
        raise RuntimeError(
            "TigerGraph connection failed"
        )

    result = benchmark_mixed_worker(
        adapter=adapter,
        node_ids=node_ids,
        operations=operations
    )

    adapter.close()

    return result


def run_concurrency_test(
    node_ids,
    workers,
    operations_per_worker
):

    print("\n" + "=" * 60)

    print(
        f"TigerGraph Mixed Workload"
    )

    print(
        f"Concurrency: {workers}"
    )

    print(
        f"Operations per worker: "
        f"{operations_per_worker}"
    )

    print(
        f"Total operations: "
        f"{workers * operations_per_worker}"
    )

    print("=" * 60)

    start_time = time.perf_counter()

    results = []

    with ThreadPoolExecutor(
        max_workers=workers
    ) as executor:

        futures = [
            executor.submit(
                run_worker,
                node_ids,
                operations_per_worker
            )
            for _ in range(workers)
        ]

        for future in futures:

            results.append(
                future.result()
            )

    total_time = (
        time.perf_counter()
        - start_time
    )

    # ---------------------------------------------
    # Combine results
    # ---------------------------------------------

    latencies = []

    reads = 0
    writes = 0
    errors = 0

    for result in results:

        latencies.extend(
            result["latencies"]
        )

        reads += result["reads"]
        writes += result["writes"]
        errors += result["errors"]

    total_operations = (
        reads + writes + errors
    )

    successful_operations = (
        reads + writes
    )

    # ---------------------------------------------
    # Results
    # ---------------------------------------------

    print("\n=== Result ===")

    print(
        f"Concurrency: {workers}"
    )

    print(
        f"Total operations: "
        f"{total_operations}"
    )

    print(
        f"Successful operations: "
        f"{successful_operations}"
    )

    print(
        f"Reads: {reads}"
    )

    print(
        f"Writes: {writes}"
    )

    print(
        f"Errors: {errors}"
    )

    print(
        f"Total time: "
        f"{total_time:.4f} sec"
    )

    if latencies:

        print(
            f"p50: "
            f"{percentile(latencies, 50):.4f} ms"
        )

        print(
            f"p95: "
            f"{percentile(latencies, 95):.4f} ms"
        )

        print(
            f"Average: "
            f"{statistics.mean(latencies):.4f} ms"
        )

        print(
            f"Min: "
            f"{min(latencies):.4f} ms"
        )

        print(
            f"Max: "
            f"{max(latencies):.4f} ms"
        )

    # ---------------------------------------------
    # Throughput
    # ---------------------------------------------

    if total_time > 0:

        throughput = (
            successful_operations
            / total_time
        )

        print(
            f"Throughput: "
            f"{throughput:.2f} operations/sec"
        )

    return {
        "concurrency": workers,
        "total_operations": total_operations,
        "reads": reads,
        "writes": writes,
        "errors": errors,
        "total_time_seconds": total_time,
        "p50_ms": percentile(latencies, 50)
            if latencies else 0,
        "p95_ms": percentile(latencies, 95)
            if latencies else 0,
        "average_ms": statistics.mean(latencies)
            if latencies else 0,
        "min_ms": min(latencies)
            if latencies else 0,
        "max_ms": max(latencies)
            if latencies else 0,
        "throughput_ops_sec": (
            successful_operations / total_time
            if total_time > 0
            else 0
        )
    }


def main():

    # =================================================
    # DATASET
    # =================================================

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

    # =================================================
    # NODE IDS
    # =================================================

    node_ids = []

    seen = set()

    for src, dst in edges:

        for node_id in (src, dst):

            node_id = str(node_id)

            if node_id not in seen:

                seen.add(node_id)
                node_ids.append(node_id)

            if len(node_ids) == 10:
                break

        if len(node_ids) == 10:
            break

    print(
        f"Using {len(node_ids)} mixed workload nodes."
    )

    print(
        f"Node IDs: {node_ids}"
    )

    # =================================================
    # TESTS
    # =================================================

    concurrency_levels = [1, 10, 40]

    operations_per_worker = 100

    all_results = []

    for workers in concurrency_levels:

        try:

            result = run_concurrency_test(
                node_ids=node_ids,
                workers=workers,
                operations_per_worker=(
                    operations_per_worker
                )
            )

            all_results.append(result)

        except Exception as exc:

            print(
                f"\nConcurrency {workers} failed:"
            )

            print(exc)

    # =================================================
    # SUMMARY
    # =================================================

    print("\n")
    print("=" * 80)
    print("TIGERGRAPH MIXED WORKLOAD SUMMARY")
    print("=" * 80)

    print(
        f"{'Concurrency':<15}"
        f"{'p50(ms)':<15}"
        f"{'p95(ms)':<15}"
        f"{'Avg(ms)':<15}"
        f"{'Throughput':<20}"
        f"{'Errors':<10}"
    )

    print("-" * 80)

    for result in all_results:

        print(
            f"{result['concurrency']:<15}"
            f"{result['p50_ms']:<15.4f}"
            f"{result['p95_ms']:<15.4f}"
            f"{result['average_ms']:<15.4f}"
            f"{result['throughput_ops_sec']:<20.2f}"
            f"{result['errors']:<10}"
        )

    print("=" * 80)


if __name__ == "__main__":
    main()