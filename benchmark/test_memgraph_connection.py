from benchmark.adapters.memgraph import MemgraphAdapter


def main():

    db = MemgraphAdapter()

    try:
        db.connect()

        print(
            "Memgraph adapter test successful!"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()