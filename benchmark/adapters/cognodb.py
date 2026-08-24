import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

from benchmark.adapters.base import GraphDatabaseAdapter


class CognoDBAdapter(GraphDatabaseAdapter):

    def __init__(self):

        load_dotenv()

        self.uri = os.getenv("COGNODB_URI")
        self.username = os.getenv(
            "COGNODB_USERNAME",
            "cognodb"
        )
        self.password = os.getenv(
            "COGNODB_PASSWORD"
        )
        self.database = os.getenv(
            "COGNODB_DATABASE",
            "neo4j"
        )

        if not self.uri:
            raise ValueError(
                "COGNODB_URI is missing from .env"
            )

        if not self.password:
            raise ValueError(
                "COGNODB_PASSWORD is missing from .env"
            )

        self.driver = None

    # -------------------------
    # CONNECTION
    # -------------------------

    def connect(self):

        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(
                self.username,
                self.password
            )
        )

        self.driver.verify_connectivity()

        print("Connected to CognoDB successfully!")

    # -------------------------
    # CLEAR BENCHMARK DATA
    # -------------------------

    def clear_benchmark_data(self):

        self.driver.execute_query(
            """
            MATCH (n:BenchmarkPerson)
            DETACH DELETE n
            """,
            database_=self.database
        )

        print("Benchmark data cleared.")

    # -------------------------
    # CREATE INDEX
    # -------------------------

    def create_indexes(self):

        self.driver.execute_query(
            """
            CREATE INDEX benchmark_person_id
            IF NOT EXISTS
            FOR (p:BenchmarkPerson)
            ON (p.id)
            """,
            database_=self.database
        )

        print("Benchmark index created.")

    # -------------------------
    # LOAD DATA
    # -------------------------

    def load_data(
        self,
        edges,
        batch_size=1000
    ):

        query = """
        UNWIND $rows AS row

        MERGE (a:BenchmarkPerson {
            id: row.src
        })

        MERGE (b:BenchmarkPerson {
            id: row.dst
        })

        MERGE (a)-[:BENCHMARK_KNOWS]->(b)
        """

        for i in range(
            0,
            len(edges),
            batch_size
        ):

            batch = edges[
                i:i + batch_size
            ]

            rows = [
                {
                    "src": src,
                    "dst": dst
                }
                for src, dst in batch
            ]

            self.driver.execute_query(
                query,
                rows=rows,
                database_=self.database
            )

    # -------------------------
    # GET START NODES
    # -------------------------

    def get_start_nodes(
        self,
        limit=1000
    ):

        records, _, _ = self.driver.execute_query(
            """
            MATCH (p:BenchmarkPerson)

            RETURN p.id AS id

            ORDER BY p.id

            LIMIT $limit
            """,
            limit=limit,
            database_=self.database
        )

        return [
            record["id"]
            for record in records
        ]

    # -------------------------
    # TRAVERSAL
    # -------------------------

    def traversal(
        self,
        node_id,
        hops
    ):

        patterns = {

            1: """
            -[:BENCHMARK_KNOWS]->
            """,

            2: """
            -[:BENCHMARK_KNOWS]->
            ()-[:BENCHMARK_KNOWS]->
            """,

            3: """
            -[:BENCHMARK_KNOWS]->
            ()-[:BENCHMARK_KNOWS]->
            ()-[:BENCHMARK_KNOWS]->
            """
        }

        if hops not in patterns:
            raise ValueError(
                "Only 1, 2 and 3 hops are supported"
            )

        query = f"""
        MATCH (
            p:BenchmarkPerson {{
                id: $id
            }}
        )
        {patterns[hops]}
        (target:BenchmarkPerson)

        RETURN count(target) AS count
        """

        records, _, _ = self.driver.execute_query(
            query,
            id=node_id,
            database_=self.database
        )

        return records[0]["count"]

    # -------------------------
    # POINT LOOKUP
    # -------------------------

    def point_lookup(
        self,
        node_id
    ):

        records, _, _ = self.driver.execute_query(
            """
            MATCH (p:BenchmarkPerson)

            WHERE p.id = $id

            RETURN p.id AS id

            LIMIT 1
            """,
            id=node_id,
            database_=self.database
        )

        return (
            records[0]["id"]
            if records
            else None
        )

    # -------------------------
    # INDEXED LOOKUP
    # -------------------------

    def indexed_lookup(
        self,
        node_id
    ):

        records, _, _ = self.driver.execute_query(
            """
            MATCH (
                p:BenchmarkPerson {
                    id: $id
                }
            )

            RETURN p.id AS id

            LIMIT 1
            """,
            id=node_id,
            database_=self.database
        )

        return (
            records[0]["id"]
            if records
            else None
        )

    # -------------------------
    # AGGREGATION
    # -------------------------

    def aggregation(self):

        records, _, _ = self.driver.execute_query(
            """
            MATCH (
                p:BenchmarkPerson
            )-[:BENCHMARK_KNOWS]->()

            RETURN
                p.id AS id,
                count(*) AS degree

            ORDER BY degree DESC

            LIMIT 100
            """,
            database_=self.database
        )

        return len(records)

    # -------------------------
    # MIXED READ
    # -------------------------

    def mixed_read(
        self,
        node_id
    ):

        return self.point_lookup(
            node_id
        )

    # -------------------------
    # MIXED WRITE
    # -------------------------

    def mixed_write(
        self,
        src,
        dst
    ):

        self.driver.execute_query(
            """
            MERGE (
                a:BenchmarkPerson {
                    id: $src
                }
            )

            MERGE (
                b:BenchmarkPerson {
                    id: $dst
                }
            )

            MERGE (
                a
            )-[:BENCHMARK_KNOWS]->(
                b
            )
            """,
            src=src,
            dst=dst,
            database_=self.database
        )

    # -------------------------
    # CLOSE
    # -------------------------

    def close(self):

        if self.driver:

            self.driver.close()

            print("Connection closed.")