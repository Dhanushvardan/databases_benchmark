from benchmark.adapters.cognodb import CognoDBAdapter


def main():

    db = CognoDBAdapter()

    try:

        db.connect()

        db.clear_benchmark_data()

        edges = [
            (1, 2),
            (2, 3),
            (3, 4),
            (1, 5),
            (5, 6)
        ]

        db.load_data(edges)

        db.create_indexes()

        nodes = db.get_start_nodes()

        print("Start nodes:")
        print(nodes)

        print(
            "1-hop:",
            db.traversal(1, 1)
        )

        print(
            "2-hop:",
            db.traversal(1, 2)
        )

        print(
            "Point lookup:",
            db.point_lookup(1)
        )

        print(
            "Indexed lookup:",
            db.indexed_lookup(1)
        )

        print(
            "Aggregation:",
            db.aggregation()
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()