import os

from dotenv import load_dotenv
from arango import ArangoClient

from benchmark.adapters.base import GraphDatabaseAdapter


class ArangoDBAdapter(GraphDatabaseAdapter):

    def __init__(self):
        load_dotenv()

        self.host = os.getenv("ARANGO_HOST")
        self.username = os.getenv(
            "ARANGO_USERNAME",
            "root"
        )
        self.password = os.getenv(
            "ARANGO_PASSWORD"
        )
        self.database = os.getenv(
            "ARANGO_DATABASE",
            "_system"
        )

        if not self.host:
            raise ValueError(
                "ARANGO_HOST is missing from .env"
            )

        if not self.password:
            raise ValueError(
                "ARANGO_PASSWORD is missing from .env"
            )

        self.client = None
        self.db = None

        # =====================================================
        # COLLECTION NAMES
        # =====================================================

        self.vertex_collection = "benchmark_vertices"
        self.edge_collection = "benchmark_edges"

    # =========================================================
    # CONNECTION
    # =========================================================

    def connect(self):

        self.client = ArangoClient(
            hosts=self.host
        )

        self.db = self.client.db(
            self.database,
            username=self.username,
            password=self.password
        )

        # Verify connection
        self.db.version()

        print(
            "Connected to ArangoDB successfully!"
        )

    # =========================================================
    # CLEAR BENCHMARK DATA
    # =========================================================

    def clear_benchmark_data(self):

        if self.db.has_collection(
            self.vertex_collection
        ):
            self.db.delete_collection(
                self.vertex_collection
            )

        if self.db.has_collection(
            self.edge_collection
        ):
            self.db.delete_collection(
                self.edge_collection
            )

        print(
            "Benchmark data cleared."
        )

    # =========================================================
    # CREATE COLLECTIONS / INDEXES
    # =========================================================

    def create_indexes(self):

        # -----------------------------------------------------
        # Vertex collection
        # -----------------------------------------------------

        if not self.db.has_collection(
            self.vertex_collection
        ):
            vertices = self.db.create_collection(
                self.vertex_collection
            )
        else:
            vertices = self.db.collection(
                self.vertex_collection
            )

        # -----------------------------------------------------
        # Edge collection
        # -----------------------------------------------------

        if not self.db.has_collection(
            self.edge_collection
        ):
            self.db.create_collection(
                self.edge_collection,
                edge=True
            )

        # -----------------------------------------------------
        # Hash index on vertex.id
        # -----------------------------------------------------

        try:

            vertices.add_hash_index(
                fields=["id"],
                unique=True
            )

        except Exception:

            # Index already exists
            pass

        print(
            "Benchmark collections and indexes created."
        )

    # =========================================================
    # LOAD DATA
    # =========================================================

    def load_data(
        self,
        edges,
        batch_size=5000
    ):

        vertices = self.db.collection(
            self.vertex_collection
        )

        edge_collection = self.db.collection(
            self.edge_collection
        )

        # =====================================================
        # COLLECT UNIQUE VERTICES
        # =====================================================

        vertex_ids = set()

        for src, dst in edges:

            vertex_ids.add(
                str(src)
            )

            vertex_ids.add(
                str(dst)
            )

        print(
            f"Unique vertices found: "
            f"{len(vertex_ids)}"
        )

        # =====================================================
        # INSERT VERTICES
        # =====================================================

        vertex_documents = [
            {
                "_key": node_id,
                "id": node_id
            }
            for node_id in vertex_ids
        ]

        print(
            f"Inserting "
            f"{len(vertex_documents)} vertices..."
        )

        for i in range(
            0,
            len(vertex_documents),
            batch_size
        ):

            batch = vertex_documents[
                i:i + batch_size
            ]

            try:

                result = vertices.insert_many(
                    batch,
                    overwrite=False,
                    return_new=False,
                    silent=False
                )

                print(
                    f"Inserted vertex batch "
                    f"{i + 1}-"
                    f"{min(i + len(batch), len(vertex_documents))}"
                )

            except Exception as exc:

                print(
                    f"Vertex batch failed: {exc}"
                )

                raise

        # =====================================================
        # VERIFY VERTICES
        # =====================================================

        actual_vertices = vertices.count()

        print(
            f"Verified vertex documents: "
            f"{actual_vertices}"
        )

        # =====================================================
        # INSERT EDGES
        # =====================================================

        edge_documents = []

        print(
            f"Inserting {len(edges)} edges..."
        )

        inserted_edges = 0

        for src, dst in edges:

            src = str(src)
            dst = str(dst)

            edge_documents.append(
                {
                    "_from": (
                        f"{self.vertex_collection}/{src}"
                    ),
                    "_to": (
                        f"{self.vertex_collection}/{dst}"
                    ),
                    "src": src,
                    "dst": dst
                }
            )

            if len(edge_documents) >= batch_size:

                try:

                    result = edge_collection.insert_many(
                        edge_documents,
                        overwrite=False,
                        return_new=False,
                        silent=False
                    )

                    inserted_edges += len(
                        edge_documents
                    )

                    print(
                        f"Inserted edge documents: "
                        f"{inserted_edges}/"
                        f"{len(edges)}"
                    )

                except Exception as exc:

                    print(
                        f"Edge batch failed: {exc}"
                    )

                    raise

                edge_documents = []

        # =====================================================
        # REMAINING EDGES
        # =====================================================

        if edge_documents:

            try:

                result = edge_collection.insert_many(
                    edge_documents,
                    overwrite=False,
                    return_new=False,
                    silent=False
                )

                inserted_edges += len(
                    edge_documents
                )

                print(
                    f"Inserted edge documents: "
                    f"{inserted_edges}/"
                    f"{len(edges)}"
                )

            except Exception as exc:

                print(
                    f"Final edge batch failed: {exc}"
                )

                raise

        # =====================================================
        # VERIFY EDGES
        # =====================================================

        actual_edges = edge_collection.count()

        print(
            f"Verified edge documents: "
            f"{actual_edges}"
        )

        # =====================================================
        # FINAL LOAD VERIFICATION
        # =====================================================

        print()
        print(
            "=== LOAD VERIFICATION ==="
        )

        print(
            f"Expected vertices: "
            f"{len(vertex_documents)}"
        )

        print(
            f"Actual vertices: "
            f"{actual_vertices}"
        )

        print(
            f"Expected edges: "
            f"{len(edges)}"
        )

        print(
            f"Actual edges: "
            f"{actual_edges}"
        )

        print()

    # =========================================================
    # GET START NODES
    # =========================================================

    def get_start_nodes(
        self,
        limit=1000
    ):

        query = f"""
        FOR v IN {self.vertex_collection}

            SORT v.id

            LIMIT @limit

            RETURN v.id
        """

        cursor = self.db.aql.execute(
            query,
            bind_vars={
                "limit": limit
            }
        )

        return list(cursor)

    # =========================================================
    # TRAVERSAL
    # =========================================================

    def traversal(
        self,
        node_id,
        hops
    ):

        if hops not in [1, 2, 3]:

            raise ValueError(
                "Only 1, 2 and 3 hops are supported"
            )

        query = f"""
        WITH {self.vertex_collection}

        FOR v IN 1..{hops}

            OUTBOUND @start

            {self.edge_collection}

            RETURN v
        """

        start_vertex = (
            f"{self.vertex_collection}/{node_id}"
        )

        cursor = self.db.aql.execute(
            query,
            bind_vars={
                "start": start_vertex
            }
        )

        return len(
            list(cursor)
        )

    # =========================================================
    # POINT LOOKUP
    # =========================================================

    def point_lookup(
        self,
        node_id
    ):

        query = f"""
        FOR v IN {self.vertex_collection}

            FILTER v.id == @id

            LIMIT 1

            RETURN v.id
        """

        cursor = self.db.aql.execute(
            query,
            bind_vars={
                "id": str(node_id)
            }
        )

        records = list(cursor)

        if records:
            return records[0]

        return None

    # =========================================================
    # INDEXED LOOKUP
    # =========================================================

    def indexed_lookup(
        self,
        node_id
    ):

        query = f"""
        FOR v IN {self.vertex_collection}

            FILTER v.id == @id

            LIMIT 1

            RETURN v.id
        """

        cursor = self.db.aql.execute(
            query,
            bind_vars={
                "id": str(node_id)
            }
        )

        records = list(cursor)

        if records:
            return records[0]

        return None

    # =========================================================
    # AGGREGATION
    # =========================================================

    def aggregation(self):

        query = f"""
        FOR v IN {self.vertex_collection}

            LET degree = LENGTH(

                FOR neighbor IN 1..1

                    OUTBOUND v

                    {self.edge_collection}

                    RETURN neighbor
            )

            SORT degree DESC

            LIMIT 100

            RETURN {{
                id: v.id,
                degree: degree
            }}
        """

        cursor = self.db.aql.execute(
            query
        )

        records = list(cursor)

        return len(records)

    # =========================================================
    # MIXED READ
    # =========================================================

    def mixed_read(
        self,
        node_id
    ):

        return self.point_lookup(
            node_id
        )

    # =========================================================
    # MIXED WRITE
    # =========================================================

    def mixed_write(
        self,
        src,
        dst
    ):

        src = str(src)
        dst = str(dst)

        source_vertex = (
            f"{self.vertex_collection}/{src}"
        )

        destination_vertex = (
            f"{self.vertex_collection}/{dst}"
        )

        # =====================================================
        # 1. UPSERT SOURCE VERTEX
        # =====================================================

        source_query = f"""
        UPSERT {{
            _key: @key
        }}

        INSERT {{
            _key: @key,
            id: @key
        }}

        UPDATE {{}}

        IN {self.vertex_collection}
        """

        self.db.aql.execute(
            source_query,
            bind_vars={
                "key": src
            }
        )

        # =====================================================
        # 2. UPSERT DESTINATION VERTEX
        # =====================================================

        destination_query = f"""
        UPSERT {{
            _key: @key
        }}

        INSERT {{
            _key: @key,
            id: @key
        }}

        UPDATE {{}}

        IN {self.vertex_collection}
        """

        self.db.aql.execute(
            destination_query,
            bind_vars={
                "key": dst
            }
        )

        # =====================================================
        # 3. CHECK + INSERT EDGE
        # =====================================================

        edge_query = f"""
        LET existing = FIRST(

            FOR e IN {self.edge_collection}

                FILTER e._from == @source
                AND e._to == @destination

                LIMIT 1

                RETURN e
        )

        FILTER existing == null

        INSERT {{
            _from: @source,
            _to: @destination,
            src: @src,
            dst: @dst
        }}

        INTO {self.edge_collection}
        """

        self.db.aql.execute(
            edge_query,
            bind_vars={
                "source": source_vertex,
                "destination": destination_vertex,
                "src": src,
                "dst": dst
            }
        )

    # =========================================================
    # FOOTPRINT
    # =========================================================

    def footprint(self):

        vertex_collection = self.db.collection(
            self.vertex_collection
        )

        edge_collection = self.db.collection(
            self.edge_collection
        )

        # =====================================================
        # ACTUAL DOCUMENT COUNTS
        # =====================================================

        vertex_count = (
            vertex_collection.count()
        )

        edge_count = (
            edge_collection.count()
        )

        # =====================================================
        # COLLECTION STATISTICS
        # =====================================================

        vertex_stats = (
            vertex_collection.statistics()
        )

        edge_stats = (
            edge_collection.statistics()
        )

        # =====================================================
        # DEBUG STATISTICS
        # =====================================================

        print()
        print(
            "Vertex statistics:"
        )

        print(
            vertex_stats
        )

        print()
        print(
            "Edge statistics:"
        )

        print(
            edge_stats
        )

        # =====================================================
        # EXTRACT STORAGE SIZE
        # =====================================================

        def extract_size(stats):

            if not stats:
                return 0

            # -------------------------------------------------
            # Direct statistics keys
            # -------------------------------------------------

            possible_keys = [
                "documentsSize",
                "documents_size",
                "dataSize",
                "data_size"
            ]

            for key in possible_keys:

                value = stats.get(key)

                if isinstance(
                    value,
                    (int, float)
                ):

                    return int(value)

            # -------------------------------------------------
            # Figures
            # -------------------------------------------------

            figures = stats.get(
                "figures",
                {}
            )

            if isinstance(
                figures,
                dict
            ):

                for key in possible_keys:

                    value = figures.get(key)

                    if isinstance(
                        value,
                        (int, float)
                    ):

                        return int(value)

            return 0

        vertex_size = extract_size(
            vertex_stats
        )

        edge_size = extract_size(
            edge_stats
        )

        # =====================================================
        # TOTAL SIZE
        # =====================================================

        total_size = (
            vertex_size +
            edge_size
        )

        total_size_mb = (
            total_size /
            (1024 * 1024)
        )

        # =====================================================
        # RESULT
        # =====================================================

        return {

            "vertex_documents":
                vertex_count,

            "edge_documents":
                edge_count,

            "vertex_size_bytes":
                vertex_size,

            "edge_size_bytes":
                edge_size,

            "total_size_bytes":
                total_size,

            "total_size_mb":
                total_size_mb
        }

    # =========================================================
    # CLOSE
    # =========================================================

    def close(self):

        self.client = None
        self.db = None

        print(
            "Connection closed."
        )