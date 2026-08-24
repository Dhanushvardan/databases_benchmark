from benchmark.adapters.neo4j import Neo4jAdapter


def main():

    db = Neo4jAdapter()

    try:

        db.connect()

    finally:

        db.close()


if __name__ == "__main__":
    main()