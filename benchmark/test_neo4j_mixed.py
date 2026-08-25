import json
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from benchmark.adapters.neo4j import Neo4jAdapter
from benchmark.workloads.mixed import benchmark_mixed_worker


def percentile(values, percentile_value):
    values = sorted(values)

    index = int(
        (percentile_value / 100) * len(values)
    )

    index = min(
        index,
        len(values) - 1
    )

    return values[index]


def run_client(node_ids, operations):
    db = Neo4jAdapter()

    try:
        db.connect()

        return benchmark_mixed_worker(
            db,
            node_ids,
            operations
        )

    finally:
        db.close()


def run_mixed_benchmark(
    node_ids,
    concurrency,
    operations_per_client=100
):
    total_operations = (
        concurrency * operations_per_client
    )

    print()
    print("=" * 50)
    print(f"Running {concurrency}-client workload")
    print("=" * 50)

    print(
        f"Operations per client: "
        f"{operations_per_client}"
    )

    print(
        f"Total operations: "
        f"{total_operations}"
    )

    # -------------------------
    # Run workload
    # -------------------------

    start = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=concurrency
    ) as executor:

        futures = [
            executor.submit(
                run_client,
                node_ids,
                operations_per_client
            )
            for _ in range(concurrency)
        ]

        results = [
            future.result()
            for future in futures
        ]

    elapsed = (
        time.perf_counter() - start
    )

    # -------------------------
    # Aggregate results
    # -------------------------

    all_latencies = []

    total_reads = 0
    total_writes = 0
    total_errors = 0

    for result in results:

        all_latencies.extend(
            result["latencies"]
        )

        total_reads += result["reads"]
        total_writes += result["writes"]
        total_errors += result["errors"]

    successful_operations = (
        total_reads + total_writes
    )

    throughput = (
        successful_operations / elapsed
        if elapsed > 0
        else 0
    )

    read_percentage = (
        total_reads /
        successful_operations *
        100
        if successful_operations > 0
        else 0
    )

    write_percentage = (
        total_writes /
        successful_operations *
        100
        if successful_operations > 0
        else 0
    )

    # -------------------------
    # Latency
    # -------------------------

    p50 = percentile(
        all_latencies,
        50
    )

    p95 = percentile(
        all_latencies,
        95
    )

    average = statistics.mean(
        all_latencies
    )

    # -------------------------
    # Print
    # -------------------------

    print()
    print(
        f"Clients: {concurrency}"
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
        f"Errors: {total_errors}"
    )

    print(
        f"Reads: {total_reads} "
        f"({read_percentage:.2f}%)"
    )

    print(
        f"Writes: {total_writes} "
        f"({write_percentage:.2f}%)"
    )

    print(
        f"Total time: "
        f"{elapsed:.4f} seconds"
    )

    print(
        f"Throughput: "
        f"{throughput:.2f} ops/sec"
    )

    print(
        f"p50: {p50:.4f} ms"
    )

    print(
        f"p95: {p95:.4f} ms"
    )

    print(
        f"Average: {average:.4f} ms"
    )

    return {
        "concurrency": concurrency,
        "operations_per_client":
            operations_per_client,
        "total_operations":
            total_operations,
        "successful_operations":
            successful_operations,
        "errors": total_errors,
        "reads": total_reads,
        "writes": total_writes,
        "read_percentage":
            read_percentage,
        "write_percentage":
            write_percentage,
        "elapsed_seconds":
            elapsed,
        "throughput_ops_per_sec":
            throughput,
        "p50_ms":
            p50,
        "p95_ms":
            p95,
        "average_ms":
            average
    }


def main():

    # -------------------------
    # Setup connection
    # -------------------------

    setup_db = Neo4jAdapter()

    try:
        setup_db.connect()
        setup_db.create_indexes()

        node_ids = setup_db.get_start_nodes(
            limit=100
        )

    finally:
        setup_db.close()

    print(
        f"Using {len(node_ids)} nodes."
    )

    # -------------------------
    # Run all concurrency levels
    # -------------------------

    results = []

    for concurrency in [1, 10, 40]:

        result = run_mixed_benchmark(
            node_ids,
            concurrency,
            operations_per_client=100
        )

        results.append(result)

    # -------------------------
    # Save results
    # -------------------------

    output_dir = Path(
        "results/raw"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir /
        "neo4j_mixed.json"
    )

    output = {
        "database": "neo4j",
        "read_write_mix_target": "80/20",
        "results": results
    }

    with output_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4
        )

    print()
    print("=" * 50)
    print(
        f"Results saved to {output_file}"
    )
    print("=" * 50)


if __name__ == "__main__":
    main()