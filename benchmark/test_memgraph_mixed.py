import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from benchmark.adapters.memgraph import MemgraphAdapter
from benchmark.workloads.mixed import benchmark_mixed_worker


def run_client(node_ids, operations):
    db = MemgraphAdapter()

    try:
        db.connect()

        return benchmark_mixed_worker(
            db,
            node_ids,
            operations
        )

    finally:
        db.close()


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


def run_workload(
    node_ids,
    clients,
    operations_per_client
):

    total_operations = (
        clients * operations_per_client
    )

    print()
    print("=" * 50)
    print(
        f"Running {clients}-client workload"
    )
    print("=" * 50)

    print(
        f"Operations per client: "
        f"{operations_per_client}"
    )

    print(
        f"Total operations: "
        f"{total_operations}"
    )

    import time

    start = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=clients
    ) as executor:

        futures = [
            executor.submit(
                run_client,
                node_ids,
                operations_per_client
            )
            for _ in range(clients)
        ]

        results = [
            future.result()
            for future in futures
        ]

    elapsed = (
        time.perf_counter() - start
    )

    all_latencies = []

    reads = 0
    writes = 0
    errors = 0

    for result in results:

        all_latencies.extend(
            result["latencies"]
        )

        reads += result["reads"]
        writes += result["writes"]
        errors += result["errors"]

    successful = (
        reads + writes
    )

    throughput = (
        successful / elapsed
        if elapsed > 0
        else 0
    )

    result = {
        "clients": clients,
        "operations_per_client":
            operations_per_client,
        "total_operations":
            total_operations,
        "successful_operations":
            successful,
        "errors":
            errors,
        "reads":
            reads,
        "writes":
            writes,
        "total_time_seconds":
            elapsed,
        "throughput_ops_per_sec":
            throughput,
        "p50_ms":
            percentile(
                all_latencies,
                50
            ),
        "p95_ms":
            percentile(
                all_latencies,
                95
            ),
        "average_ms":
            sum(all_latencies)
            / len(all_latencies)
    }

    print()
    print(
        f"Clients: {clients}"
    )

    print(
        f"Total operations: "
        f"{total_operations}"
    )

    print(
        f"Successful operations: "
        f"{successful}"
    )

    print(
        f"Errors: {errors}"
    )

    print(
        f"Reads: {reads} "
        f"({reads / successful * 100:.2f}%)"
    )

    print(
        f"Writes: {writes} "
        f"({writes / successful * 100:.2f}%)"
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

    return result


def main():

    db = MemgraphAdapter()

    try:

        db.connect()
        db.create_indexes()

        node_ids = db.get_start_nodes(
            limit=100
        )

        print(
            f"Using {len(node_ids)} nodes."
        )

    finally:
        db.close()

    workloads = {}

    for clients in [1, 10, 40]:

        workloads[
            f"{clients}_clients"
        ] = run_workload(
            node_ids,
            clients,
            100
        )

    output_dir = Path(
        "results/raw"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir /
        "memgraph_mixed.json"
    )

    output = {
        "database": "memgraph",
        "workload": "80_percent_read_20_percent_write",
        "node_count": len(node_ids),
        "workloads": workloads
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