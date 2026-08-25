import os
import platform
import sys
import psutil


def measure_client_footprint():
    """
    Measure the footprint of the benchmark client process.

    Note:
    This measures Python/client memory, NOT database server memory.
    """

    process = psutil.Process(os.getpid())

    memory_info = process.memory_info()

    memory_mb = (
        memory_info.rss /
        (1024 * 1024)
    )

    return {
        "client_memory_mb": round(
            memory_mb,
            2
        ),
        "platform": platform.platform(),
        "python_version": sys.version.split()[0],
        "cpu_count": os.cpu_count()
    }


def measure_dataset_footprint(adapter):
    """
    Measure logical dataset size exposed through Cypher.
    """

    result = {}

    try:
        records, _, _ = adapter.driver.execute_query(
            """
            MATCH (n:BenchmarkPerson)
            RETURN count(n) AS nodes
            """,
            database_=adapter.database
        )

        result["nodes"] = records[0]["nodes"]

    except Exception as e:

        result["nodes"] = "not observable"
        result["nodes_error"] = str(e)

    try:
        records, _, _ = adapter.driver.execute_query(
            """
            MATCH ()-[r:BENCHMARK_KNOWS]->()
            RETURN count(r) AS relationships
            """,
            database_=adapter.database
        )

        result["relationships"] = records[0]["relationships"]

    except Exception as e:

        result["relationships"] = "not observable"
        result["relationships_error"] = str(e)

    return result


def benchmark_footprint(adapter):
    """
    Collect all footprint metrics available
    through the database adapter.
    """

    dataset = measure_dataset_footprint(
        adapter
    )

    client = measure_client_footprint()

    return {
        "dataset": dataset,
        "client": client
    }