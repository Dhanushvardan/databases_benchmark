from benchmark.adapters.cognodb import CognoDBAdapter


def main():

    db = CognoDBAdapter()

    try:

        db.connect()

    except Exception as e:

        print("CognoDB connection failed:")
        print(e)

    finally:

        db.close()


if __name__ == "__main__":
    main()