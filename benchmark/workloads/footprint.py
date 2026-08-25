import platform
import psutil


def benchmark_footprint(adapter):
    """
    Measure graph size and client-side process footprint.
    """

    nodes = adapter.get_node_count()
    relationships = adapter.get_relationship_count()

    process = psutil.Process()

    memory_mb = (
        process.memory_info().rss
        / (1024 * 1024)
    )

    return {
        "nodes": nodes,
        "relationships": relationships,
        "client_memory_mb": memory_mb,
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
    }