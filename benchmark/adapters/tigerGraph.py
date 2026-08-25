import os
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
import pyTigerGraph as tg
from dotenv import load_dotenv


load_dotenv()


class TigerGraphAdapter:
    """
    TigerGraph adapter for graph database benchmarking.

    Environment variables:
        TIGERGRAPH_HOST
        TIGERGRAPH_GRAPH
        TIGERGRAPH_SECRET

    Graph schema:

        node
          |
          | RELATES_TO
          v
        node
    """

    def __init__(
        self,
        host: Optional[str] = None,
        graph_name: Optional[str] = None,
        secret: Optional[str] = None,
    ):
        self.host = (
            host
            or os.getenv("TIGERGRAPH_HOST")
        )

        self.graph_name = (
            graph_name
            or os.getenv("TIGERGRAPH_GRAPH")
        )

        self.secret = (
            secret
            or os.getenv("TIGERGRAPH_SECRET")
        )

        if not self.host:
            raise ValueError(
                "TIGERGRAPH_HOST is not set"
            )

        if not self.graph_name:
            raise ValueError(
                "TIGERGRAPH_GRAPH is not set"
            )

        if not self.secret:
            raise ValueError(
                "TIGERGRAPH_SECRET is not set"
            )

        self.conn = None
        self.token = None
        self.connected = False

    # =========================================================
    # CONNECTION
    # =========================================================

    def connect(self):
        if self.connected:
            return self.conn

        print("Connecting to TigerGraph...")

        self.conn = tg.TigerGraphConnection(
            host=self.host,
            graphname=self.graph_name,
            gsqlSecret=self.secret,
        )

        self.token = self.conn.getToken(
            self.secret
        )

        # pyTigerGraph can return the token as a
        # tuple/list depending on version.
        if isinstance(self.token, (tuple, list)):
            self.token = self.token[0]

        self.connected = True

        return self.conn

    def test_connection(self) -> bool:
        try:
            self.connect()

            result = self.conn.echo()

            return result is not None

        except Exception as exc:
            print(
                f"TigerGraph connection failed: {exc}"
            )
            return False

    # =========================================================
    # SCHEMA
    # =========================================================

    def get_schema(self):
        self.connect()

        try:
            return self.conn.getSchema()

        except Exception as exc:
            print(
                f"Schema retrieval failed: {exc}"
            )
            return None

    # =========================================================
    # VERTEX
    # =========================================================

    def upsert_vertex(
        self,
        vertex_type: str,
        vertex_id: str,
        attributes: Optional[
            Dict[str, Any]
        ] = None,
    ):
        self.connect()

        attributes = attributes or {}

        return self.conn.upsertVertex(
            vertex_type,
            str(vertex_id),
            attributes,
        )

    def upsert_vertices(
        self,
        vertex_type: str,
        vertices: List[Dict[str, Any]],
    ):
        self.connect()

        results = []

        for vertex in vertices:

            vertex_id = str(
                vertex["id"]
            )

            attributes = {
                key: value
                for key, value in vertex.items()
                if key != "id"
            }

            result = self.conn.upsertVertex(
                vertex_type,
                vertex_id,
                attributes,
            )

            results.append(result)

        return results

    # =========================================================
    # EDGE
    # =========================================================

    def upsert_edge(
        self,
        edge_type: str,
        from_id: str,
        to_id: str,
        attributes: Optional[
            Dict[str, Any]
        ] = None,
    ):
        self.connect()

        attributes = attributes or {}

        return self.conn.upsertEdge(
            "node",
            str(from_id),
            edge_type,
            "node",
            str(to_id),
            attributes,
        )

    # =========================================================
    # BULK LOADING
    # =========================================================

    def load_data(
        self,
        edges: List[Tuple[int, int]],
    ):
        """
        Load unique node vertices and RELATES_TO edges.
        """

        self.connect()

        if not edges:
            return {
                "vertices": 0,
                "edges": 0,
                "batches": 0,
            }

        # -----------------------------------------------------
        # Unique vertices
        # -----------------------------------------------------

        unique_nodes = set()

        for src, dst in edges:
            unique_nodes.add(str(src))
            unique_nodes.add(str(dst))

        print(
            f"Found {len(unique_nodes)} unique node vertices."
        )

        # -----------------------------------------------------
        # HTTP headers
        # -----------------------------------------------------

        token = self.token

        if isinstance(token, (tuple, list)):
            token = token[0]

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        url = (
            f"{self.host.rstrip('/')}"
            f"/restpp/graph/{self.graph_name}"
        )

        # -----------------------------------------------------
        # Load vertices
        # -----------------------------------------------------

        print("\nLoading node vertices...")

        vertex_batch_size = 5000

        node_list = list(unique_nodes)

        total_vertices = len(node_list)

        total_vertex_batches = (
            total_vertices
            + vertex_batch_size
            - 1
        ) // vertex_batch_size

        loaded_vertices = 0

        for batch_number, start in enumerate(
            range(
                0,
                total_vertices,
                vertex_batch_size,
            ),
            start=1,
        ):

            batch = node_list[
                start:start + vertex_batch_size
            ]

            payload = {
                "vertices": {
                    "node": {
                        node_id: {}
                        for node_id in batch
                    }
                }
            }

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=120,
            )

            if response.status_code not in (
                200,
                201,
            ):
                raise RuntimeError(
                    "TigerGraph vertex loading failed "
                    f"with HTTP "
                    f"{response.status_code}: "
                    f"{response.text}"
                )

            loaded_vertices += len(batch)

            print(
                f"Loaded vertices "
                f"{loaded_vertices}/"
                f"{total_vertices} "
                f"({batch_number}/"
                f"{total_vertex_batches})"
            )

        # -----------------------------------------------------
        # Load edges
        # -----------------------------------------------------

        print(
            "\nLoading RELATES_TO edges..."
        )

        batch_size = 5000

        total_edges = len(edges)

        total_batches = (
            total_edges
            + batch_size
            - 1
        ) // batch_size

        loaded_edges = 0

        for batch_number, start in enumerate(
            range(
                0,
                total_edges,
                batch_size,
            ),
            start=1,
        ):

            batch = edges[
                start:start + batch_size
            ]

            edge_list = []

            for src, dst in batch:

                edge_list.append(
                    {
                        "from_id": str(src),
                        "to_id": str(dst),
                        "attributes": {},
                    }
                )

            payload = {
                "edges": {
                    "RELATES_TO": edge_list
                }
            }

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=120,
            )

            if response.status_code not in (
                200,
                201,
            ):
                raise RuntimeError(
                    "TigerGraph edge loading failed "
                    f"with HTTP "
                    f"{response.status_code}: "
                    f"{response.text}"
                )

            loaded_edges += len(batch)

            print(
                f"Loaded edges "
                f"{loaded_edges}/"
                f"{total_edges} "
                f"({batch_number}/"
                f"{total_batches})"
            )

        return {
            "vertices": loaded_vertices,
            "edges": loaded_edges,
            "batches": total_batches,
        }

    # =========================================================
    # INSTALLED QUERY
    # =========================================================

    def run_query(
        self,
        query_name: str,
        params: Optional[
            Dict[str, Any]
        ] = None,
    ):
        self.connect()

        return self.conn.runInstalledQuery(
            query_name,
            params=params or {},
        )

    # =========================================================
    # TRAVERSAL
    # =========================================================

    def traversal(
        self,
        start_node,
        hops,
    ):
        """
        Run benchmark_traversal.

        TigerGraph VERTEX<T> parameters require
        tuple format.
        """

        self.connect()

        return self.conn.runInstalledQuery(
            "benchmark_traversal",
            params={
                "start_node": (
                    str(start_node),
                ),
                "hops": int(hops),
            },
        )

    # =========================================================
    # LOOKUP
    # =========================================================

    def lookup(self, node_id):
        """
        Point lookup using the installed
        benchmark_lookup query.
        """

        self.connect()

        return self.conn.runInstalledQuery(
            "benchmark_lookup",
            params={
                "node_id": (
                    str(node_id),
                )
            },
        )

    # =========================================================
    # AGGREGATION
    # =========================================================

    def aggregation(self):
        """
        Run the installed aggregation query.

        The aggregation query can simply return
        a count/value from the graph.
        """

        self.connect()

        return self.conn.runInstalledQuery(
            "benchmark_aggregation"
        )

    # =========================================================
    # MIXED WORKLOAD - READ
    # =========================================================

    def mixed_read(self, node_id):
        """
        Read operation for mixed workload.

        Uses benchmark_mixed_read if installed.
        """

        self.connect()

        return self.conn.runInstalledQuery(
            "benchmark_mixed_read",
            params={
                "node_id": (
                    str(node_id),
                )
            },
        )

    # =========================================================
    # MIXED WORKLOAD - WRITE
    # =========================================================

    def mixed_write(
        self,
        src,
        dst,
    ):
        """
        Write operation for mixed workload.

        Uses the TigerGraph RELATES_TO edge.
        """

        self.connect()

        return self.conn.upsertEdge(
            "node",
            str(src),
            "RELATES_TO",
            "node",
            str(dst),
            {},
        )

    # =========================================================
    # FOOTPRINT - NODE COUNT
    # =========================================================

    def get_node_count(self):
        """
        Return number of node vertices.
        """

        self.connect()

        result = self.conn.runInstalledQuery(
            "benchmark_node_count"
        )

        if not result:
            return 0

        for item in result:

            if "@@count" in item:
                return int(
                    item["@@count"]
                )

        return 0

    # =========================================================
    # FOOTPRINT - EDGE COUNT
    # =========================================================

    def get_relationship_count(self):
        """
        Return number of RELATES_TO edges.
        """

        self.connect()

        result = self.conn.runInstalledQuery(
            "benchmark_edge_count"
        )

        if not result:
            return 0

        for item in result:

            if "@@count" in item:
                return int(
                    item["@@count"]
                )

        return 0

    # =========================================================
    # GSQL
    # =========================================================

    def run_gsql(
        self,
        gsql: str,
    ):
        self.connect()

        return self.conn.gsql(gsql)

    # =========================================================
    # MEASURE
    # =========================================================

    def measure(
        self,
        operation,
        *args,
        **kwargs,
    ):

        start = time.perf_counter()

        result = operation(
            *args,
            **kwargs,
        )

        elapsed = (
            time.perf_counter()
            - start
        )

        return {
            "result": result,
            "time_seconds": elapsed,
        }

    # =========================================================
    # CLOSE
    # =========================================================

    def close(self):

        if self.conn is not None:

            if hasattr(
                self.conn,
                "close",
            ):
                try:
                    self.conn.close()
                except Exception:
                    pass

        self.conn = None
        self.token = None
        self.connected = False