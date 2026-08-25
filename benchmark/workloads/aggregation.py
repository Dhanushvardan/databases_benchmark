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


def benchmark_aggregation(
    adapter,
    warmup=20,
    iterations=100
):
    # ---------------------------------------------------------
    # Warm-up
    # ---------------------------------------------------------

    for _ in range(warmup):
        adapter.aggregation()

    # ---------------------------------------------------------
    # Measurement
    # ---------------------------------------------------------

    latencies = []

    for _ in range(iterations):

        start = time.perf_counter()

        adapter.aggregation()

        elapsed = (
            time.perf_counter()
            - start
        )

        latencies.append(
            elapsed * 1000
        )

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------

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