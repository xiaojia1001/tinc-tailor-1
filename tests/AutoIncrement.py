"""
Tests related to auto increment.
"""

from tailor.test import GenieTest
from time import sleep

class SimultaniousInsert(GenieTest):
    """Test simultanious auto-inc inserts get different numbers"""
    def setUp(self):
        if len(self.hosts.hosts) < 2:
            self.skipTest("Insufficient Hosts")
        super(SimultaniousInsert, self).setUp()
        self.master = self.hosts.hosts[0]
        self.slave = self.hosts.hosts[1]
        self.assertSqlSuccess("DROP TABLE IF EXISTS t1;", self.master, database='test')

    def runTest(self):
        self.assertSqlSuccess("CREATE TABLE t1 (c1 INT AUTO_INCREMENT PRIMARY KEY, c2 INT) ENGINE=GenieDB;", hosts=self.master, database='test')
        sleep(1)
        self.assertSqlSuccess("INSERT INTO t1 (c2) VALUES (1);", database='test')
        sleep(1)
        self.assertSqlSame("SELECT * FROM t1 ORDER BY c1 DESC;", database='test')
        self.assertSqlEqual("SELECT count(*) AS count FROM t1;", "count\n2\n", database='test')

    def tearDown(self):
        self.runSql("DROP TABLE t1;", self.master, database='test')
        super(SimultaniousInsert,self).tearDown()

class SingleNodeMultiInsert(GenieTest):
    """Test deletes are replicated"""
    def setUp(self):
        if len(self.hosts.hosts) < 1:
            self.skipTest("Insufficient Hosts")
        super(SingleNodeMultiInsert, self).setUp()
        self.master = self.hosts.hosts[0]
        self.assertSqlSuccess("DROP TABLE IF EXISTS t1;", self.master, database='test')

    def runTest(self):
        self.assertSqlSuccess("SET AUTO_INCREMENT_INCREMENT=2; SET AUTO_INCREMENT_OFFSET=3;CREATE TABLE t1 (c1 INT AUTO_INCREMENT PRIMARY KEY, c2 INT) ENGINE=GenieDB;", hosts=self.master, database='test')
        self.assertSqlSuccess("SET AUTO_INCREMENT_INCREMENT=2; SET AUTO_INCREMENT_OFFSET=3;INSERT INTO t1 (c2) VALUES (1), (2), (3);", hosts=self.master, database='test')
        sleep(1)
        self.assertSqlEqual("SELECT * FROM t1 ORDER BY c2 DESC;", "c1\tc2\n7\t3\n5\t2\n3\t1\n", database='test')

    def tearDown(self):
        self.runSql("DROP TABLE t1;", self.master, database='test')
        super(SingleNodeMultiInsert,self).tearDown()