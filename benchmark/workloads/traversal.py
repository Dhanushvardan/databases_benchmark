import time
import statistics


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


def benchmark_traversal(
    adapter,
    start_nodes,
    hops,
    warmup=20,
    iterations=100
):
    # =========================================================
    # WARM-UP
    # =========================================================

    for i in range(warmup):

        node_id = start_nodes[
            i % len(start_nodes)
        ]

        adapter.traversal(
            node_id,
            hops
        )

    # =========================================================
    # MEASUREMENT
    # =========================================================

    latencies = []

    for i in range(iterations):

        node_id = start_nodes[
            i % len(start_nodes)
        ]

        start = time.perf_counter()

        adapter.traversal(
            node_id,
            hops
        )

        elapsed = (
            time.perf_counter() - start
        )

        latencies.append(
            elapsed * 1000
        )

    # =========================================================
    # RESULTS
    # =========================================================

    return {
        "hops": hops,
        "iterations": iterations,
        "warmup": warmup,

        "p50_ms": percentile(
            latencies,
            50
        ),

        "p95_ms": percentile(
            latencies,
            95
        ),

        "average_ms": statistics.mean(
            latencies
        ),

        "min_ms": min(
            latencies
        ),

        "max_ms": max(
            latencies
        )
    }