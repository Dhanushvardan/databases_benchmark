from abc import ABC, abstractmethod


class GraphDatabaseAdapter(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def clear_benchmark_data(self):
        pass

    @abstractmethod
    def create_indexes(self):
        pass

    @abstractmethod
    def load_data(self, edges):
        pass

    @abstractmethod
    def get_start_nodes(self, limit=1000):
        pass

    @abstractmethod
    def traversal(self, node_id, hops):
        pass

    @abstractmethod
    def point_lookup(self, node_id):
        pass

    @abstractmethod
    def indexed_lookup(self, node_id):
        pass

    @abstractmethod
    def aggregation(self):
        pass

    @abstractmethod
    def mixed_read(self, node_id):
        pass

    @abstractmethod
    def mixed_write(self, src, dst):
        pass

    @abstractmethod
    def close(self):
        pass