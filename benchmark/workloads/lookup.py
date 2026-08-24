import statistics
import time


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


def benchmark_lookup(
    operation,
    node_ids,
    warmup=20,
    iterations=100
):

    # Warm-up
    for i in range(warmup):

        node_id = node_ids[
            i % len(node_ids)
        ]

        operation(node_id)

    # Measurement
    latencies = []

    for i in range(iterations):

        node_id = node_ids[
            i % len(node_ids)
        ]

        start = time.perf_counter()

        operation(node_id)

        elapsed = (
            time.perf_counter() - start
        )

        latencies.append(
            elapsed * 1000
        )

    return {
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