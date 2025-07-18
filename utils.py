from cassandra.cluster import Cluster


class CassandraUtils:

    def __init__(self):
        self.KEYSPACE = "fleet"
        cluster = Cluster(['127.0.0.1'])
        self.session = cluster.connect(keyspace=self.KEYSPACE)
