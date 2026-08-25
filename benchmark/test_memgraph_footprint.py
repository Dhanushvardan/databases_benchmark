import json
from pathlib import Path

from benchmark.adapters.memgraph import MemgraphAdapter
from benchmark.workloads.footprint import benchmark_footprint


def main():

    db = MemgraphAdapter()

    try:
        db.connect()

        print()
        print("Running Memgraph footprint benchmark...")

        result = benchmark_footprint(db)

        print()
        print("=== Memgraph Footprint Result ===")

        print(
            f"Nodes: "
            f"{result['nodes']}"
        )

        print(
            f"Relationships: "
            f"{result['relationships']}"
        )

        print(
            f"Client memory: "
            f"{result['client_memory_mb']:.2f} MB"
        )

        print(
            f"Platform: "
            f"{result['platform']}"
        )

        print(
            f"Python: "
            f"{result['python_version']}"
        )

        print(
            f"CPU count: "
            f"{result['cpu_count']}"
        )

        output = {
            "database": "memgraph",
            **result
        }

        output_dir = Path(
            "results/raw"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file = (
            output_dir /
            "memgraph_footprint.json"
        )

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
        print(
            f"Results saved to {output_file}"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()