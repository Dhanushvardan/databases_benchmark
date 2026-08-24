import csv
from pathlib import Path


INPUT_FILE = Path(
    "data/raw/soc-pokec-relationships.txt"
)

OUTPUT_FILE = Path(
    "data/processed/pokec_100k.csv"
)

TARGET_EDGES = 100_000


def prepare_dataset():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    edges = set()

    print("Reading dataset...")

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip comments
            if line.startswith("#"):
                continue

            parts = line.split()

            if len(parts) < 2:
                continue

            try:
                src = int(parts[0])
                dst = int(parts[1])
            except ValueError:
                continue

            # Avoid self-loops
            if src == dst:
                continue

            edges.add((src, dst))

            if len(edges) >= TARGET_EDGES:
                break

    edges = list(edges)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "src",
            "dst"
        ])

        writer.writerows(edges)

    print()
    print("Dataset preparation completed.")
    print(f"Input : {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Edges : {len(edges)}")


if __name__ == "__main__":
    prepare_dataset()