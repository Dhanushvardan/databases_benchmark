import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from benchmark.adapters.cognodb import CognoDBAdapter
from benchmark.workloads.mixed import (
    benchmark_mixed_worker
)


OPERATIONS_PER_CLIENT = 100


def percentile(values, percentile):

    values = sorted(values)

    if not values:
        return 0

    index = int(
        (percentile / 100) * len(values)
    )

    index = min(
        index,
        len(values) - 1
    )

    return values[index]


def create_adapter():

    adapter = CognoDBAdapter()

    adapter.connect()

    return adapter


def worker(node_ids):

    adapter = create_adapter()

    try:

        return benchmark_mixed_worker(
            adapter,
            node_ids,
            OPERATIONS_PER_CLIENT
        )

    finally:

        adapter.close()


def run_concurrency(
    node_ids,
    clients
):

    print()
    print(
        f"Running {clients} client benchmark..."
    )

    start = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=clients
    ) as executor:

        futures = [
            executor.submit(
                worker,
                node_ids
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

    total_operations = (
        total_reads +
        total_writes
    )

    throughput = (
        total_operations / elapsed
        if elapsed > 0
        else 0
    )

    return {
        "clients": clients,
        "operations": total_operations,
        "reads": total_reads,
        "writes": total_writes,
        "errors": total_errors,
        "duration_seconds": elapsed,
        "throughput_ops_per_sec": throughput,
        "p50_ms": percentile(
            all_latencies,
            50
        ),
        "p95_ms": percentile(
            all_latencies,
            95
        ),
        "average_ms": (
            statistics.mean(all_latencies)
            if all_latencies
            else 0
        )
    }


def main():

    # Temporary adapter only for getting nodes.
    db = CognoDBAdapter()

    try:

        db.connect()

        node_ids = db.get_start_nodes(
            limit=1000
        )

    finally:

        db.close()

    print(
        f"Using {len(node_ids)} nodes."
    )

    results = []

    for clients in [1, 10, 40]:

        result = run_concurrency(
            node_ids,
            clients
        )

        results.append(result)

        print()
        print(
            f"Clients: {clients}"
        )
        print(
            f"Operations: "
            f"{result['operations']}"
        )
        print(
            f"Reads: "
            f"{result['reads']}"
        )
        print(
            f"Writes: "
            f"{result['writes']}"
        )
        print(
            f"Errors: "
            f"{result['errors']}"
        )
        print(
            f"Throughput: "
            f"{result['throughput_ops_per_sec']:.2f} ops/sec"
        )
        print(
            f"p50: "
            f"{result['p50_ms']:.4f} ms"
        )
        print(
            f"p95: "
            f"{result['p95_ms']:.4f} ms"
        )

    output = Path(
        "results/raw/cognodb_concurrency.json"
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4
        )

    print()
    print(
        f"Results saved to {output}"
    )


if __name__ == "__main__":
    main()