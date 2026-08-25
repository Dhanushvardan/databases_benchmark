from benchmark.adapters.tigerGraph import TigerGraphAdapter


def main():
    print("Connecting to TigerGraph...")

    try:
        db = TigerGraphAdapter()

        if db.test_connection():
            print("TigerGraph connection successful!")
            print("TigerGraph authentication is working.")
            print(f"Graph: {db.graph_name}")
            print(f"Host: {db.host}")

        else:
            print("TigerGraph connection failed.")

    except Exception as e:
        print(f"TigerGraph connection failed: {e}")


if __name__ == "__main__":
    main()