import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

from benchmark.adapters.arangodb import ArangoDBAdapter
from benchmark.workloads.mixed import benchmark_mixed_worker


# =========================================================
# CONFIGURATION
# =========================================================

CLIENT_COUNTS = [1, 10, 40]

# Operations performed by EACH client
OPERATIONS_PER_CLIENT = 100


# =========================================================
# SINGLE CLIENT WORKER
# =========================================================

def run_client(node_ids, operations):
    """
    Each client gets its own ArangoDB connection.
    """

    adapter = ArangoDBAdapter()
    adapter.connect()

    try:
        result = benchmark_mixed_worker(
            adapter,
            node_ids,
            operations
        )

        return result

    finally:
        adapter.close()


# =========================================================
# PERCENTILE
# =========================================================

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


# =========================================================
# RUN CLIENT BENCHMARK
# =========================================================

def run_benchmark(node_ids, client_count):

    print("\n" + "=" * 60)
    print(f"RUNNING WITH {client_count} CLIENT(S)")
    print("=" * 60)

    all_latencies = []

    total_reads = 0
    total_writes = 0
    total_errors = 0

    total_operations = (
        client_count * OPERATIONS_PER_CLIENT
    )

    start_time = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=client_count
    ) as executor:

        futures = []

        for _ in range(client_count):

            future = executor.submit(
                run_client,
                node_ids,
                OPERATIONS_PER_CLIENT
            )

            futures.append(future)

        for future in as_completed(futures):

            result = future.result()

            all_latencies.extend(
                result["latencies"]
            )

            total_reads += result["reads"]
            total_writes += result["writes"]
            total_errors += result["errors"]

    total_time = (
        time.perf_counter()
        - start_time
    )

    throughput = (
        total_operations / total_time
    )

    # =====================================================
    # RESULTS
    # =====================================================

    print("\n=== ArangoDB Mixed Workload Result ===")

    print(
        f"Clients: {client_count}"
    )

    print(
        f"Operations: {total_operations}"
    )

    print(
        f"Reads: {total_reads}"
    )

    print(
        f"Writes: {total_writes}"
    )

    print(
        f"Errors: {total_errors}"
    )

    print(
        f"Read/Write ratio: "
        f"{total_reads}/{total_writes}"
    )

    print(
        f"Total time: "
        f"{total_time:.4f} sec"
    )

    print(
        f"Throughput: "
        f"{throughput:.2f} operations/sec"
    )

    print(
        f"Mixed p50: "
        f"{percentile(all_latencies, 50):.4f} ms"
    )

    print(
        f"Mixed p95: "
        f"{percentile(all_latencies, 95):.4f} ms"
    )

    print(
        f"Mixed average: "
        f"{statistics.mean(all_latencies):.4f} ms"
    )

    print(
        f"Mixed min: "
        f"{min(all_latencies):.4f} ms"
    )

    print(
        f"Mixed max: "
        f"{max(all_latencies):.4f} ms"
    )

    return {
        "clients": client_count,
        "operations": total_operations,
        "reads": total_reads,
        "writes": total_writes,
        "errors": total_errors,
        "p50_ms": percentile(
            all_latencies,
            50
        ),
        "p95_ms": percentile(
            all_latencies,
            95
        ),
        "average_ms": statistics.mean(
            all_latencies
        ),
        "min_ms": min(
            all_latencies
        ),
        "max_ms": max(
            all_latencies
        ),
        "throughput_ops_sec": throughput,
        "total_time_sec": total_time
    }


# =========================================================
# MAIN
# =========================================================

def main():

    # -----------------------------------------------------
    # Get benchmark nodes
    # -----------------------------------------------------

    adapter = ArangoDBAdapter()
    adapter.connect()

    try:

        node_ids = adapter.get_start_nodes(
            limit=100
        )

        print(
            f"Using {len(node_ids)} mixed workload nodes."
        )

    finally:

        adapter.close()

    # -----------------------------------------------------
    # Run 1, 10 and 40 clients
    # -----------------------------------------------------

    results = []

    for client_count in CLIENT_COUNTS:

        result = run_benchmark(
            node_ids,
            client_count
        )

        results.append(result)

    # =====================================================
    # FINAL SUMMARY
    # =====================================================

    print("\n")
    print("=" * 90)
    print("ARANGODB MIXED WORKLOAD - FINAL SUMMARY")
    print("=" * 90)

    print(
        f"{'Clients':<10}"
        f"{'Operations':<12}"
        f"{'Reads':<10}"
        f"{'Writes':<10}"
        f"{'Errors':<10}"
        f"{'p50(ms)':<14}"
        f"{'p95(ms)':<14}"
        f"{'Throughput':<15}"
    )

    print("-" * 90)

    for result in results:

        print(
            f"{result['clients']:<10}"
            f"{result['operations']:<12}"
            f"{result['reads']:<10}"
            f"{result['writes']:<10}"
            f"{result['errors']:<10}"
            f"{result['p50_ms']:<14.4f}"
            f"{result['p95_ms']:<14.4f}"
            f"{result['throughput_ops_sec']:<15.2f}"
        )


if __name__ == "__main__":
    main()