from benchmark.adapters.arangodb import ArangoDBAdapter


def main():
    db = ArangoDBAdapter()

    try:
        db.connect()

        print("ArangoDB connection test successful!")
        print("Database:", db.database)

    except Exception as e:
        print("ArangoDB connection failed!")
        print("Error:", e)

    finally:
        db.close()


if __name__ == "__main__":
    main()