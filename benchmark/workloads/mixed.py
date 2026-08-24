import random
import time


def run_mixed_operation(adapter, node_ids):
    """
    Run one operation.

    80% = read
    20% = write
    """

    if random.random() < 0.8:

        # READ
        node_id = random.choice(node_ids)

        adapter.mixed_read(node_id)

        return "read"

    else:

        # WRITE
        src = random.choice(node_ids)
        dst = random.choice(node_ids)

        adapter.mixed_write(
            src,
            dst
        )

        return "write"


def benchmark_mixed_worker(
    adapter,
    node_ids,
    operations
):

    latencies = []
    reads = 0
    writes = 0
    errors = 0

    for _ in range(operations):

        start = time.perf_counter()

        try:

            operation_type = run_mixed_operation(
                adapter,
                node_ids
            )

            if operation_type == "read":
                reads += 1
            else:
                writes += 1

        except Exception:

            errors += 1

        elapsed = (
            time.perf_counter() - start
        )

        latencies.append(
            elapsed * 1000
        )

    return {
        "latencies": latencies,
        "reads": reads,
        "writes": writes,
        "errors": errors
    }