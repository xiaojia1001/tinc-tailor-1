"""
Tests related to healing.
"""

from tailor.test import GenieTest
from time import sleep
try:
    from unittest.case import expectedFailure
except:
    from unittest2.case import expectedFailure

class HealingFixture(GenieTest):
    def setUp(self):
        if len(self.hosts.hosts) < 2:
            self.skipTest("Insufficient Hosts")
        super(HealingFixture, self).setUp()
        self.master = self.hosts.hosts[0]
        self.slave = self.hosts.hosts[1]
        self.assertSqlSuccess("DROP TABLE IF EXISTS t1;", self.master, database='test')
        self.assertSqlSuccess("CREATE TABLE t1 (c1 INT PRIMARY KEY, c2 INT) ENGINE=GenieDB;", hosts=self.master, database='test')

    def tearDown(self):
        self.runSql("DROP TABLE t1;", self.master, database='test')
        super(HealingFixture,self).tearDown()

class SingleRecord(HealingFixture):
    """Test conflict resolution over single record"""
    def runTest(self):
        self.partition(self.master)
        self.assertSqlSuccess("INSERT INTO t1 VALUES (1, RAND()*100000);", hosts=self.master, database='test')
        self.unpartition()
        sleep(20)
        self.assertSqlSame("SELECT * FROM t1 ORDER BY c1 DESC;", database='test')
        self.assertSqlEqual("SELECT count(*) AS count FROM t1;", "count\n1\n", database='test')


class SingleRecordWithPostWrite(HealingFixture):
    """Test conflict resolution over single record"""
    def runTest(self):
        self.partition(self.master)
        self.assertSqlSuccess("INSERT INTO t1 VALUES (1, RAND()*100000);", hosts=self.master, database='test')
        self.unpartition()
        sleep(20)
        self.assertSqlSuccess("INSERT INTO t1 VALUES (2, RAND()*100000);", hosts=self.master, database='test')
        self.assertSqlSame("SELECT * FROM t1 ORDER BY c1 DESC;", database='test')
        self.assertSqlEqual("SELECT count(*) AS count FROM t1;", "count\n2\n", database='test')

class Delete(HealingFixture):
    """Test conflict resolution over single record"""
    def runTest(self):
        self.assertSqlSuccess("INSERT INTO t1 VALUES (1, RAND()*100000);", hosts=self.master, database='test')
        self.partition(self.master)
        self.assertSqlSuccess("DELETE FROM t1 WHERE c1=1;", hosts=self.master, database='test')
        self.unpartition()
        sleep(20)
        self.assertSqlSame("SELECT * FROM t1 ORDER BY c1 DESC;", database='test')
        self.assertSqlEqual("SELECT count(*) AS count FROM t1;", "count\n0\n", database='test')

class TableCreate(GenieTest):
    """Test conflict resolution over single record"""
    def setUp(self):
        if len(self.hosts.hosts) < 2:
            self.skipTest("Insufficient Hosts")
        super(TableCreate, self).setUp()
        self.master = self.hosts.hosts[0]
        self.slave = self.hosts.hosts[1]
        self.assertSqlSuccess("DROP TABLE IF EXISTS t1;", self.master, database='test')

    def runTest(self):
        self.partition(self.master)
        self.assertSqlSuccess("CREATE TABLE t1 (c1 INT PRIMARY KEY, c2 INT) ENGINE=GenieDB;", hosts=self.master, database='test')
        self.assertSqlSuccess("INSERT INTO t1 VALUES (1, RAND()*100000);", hosts=self.master, database='test')
        self.unpartition()
        sleep(20)
        self.assertSqlSame("SHOW CREATE TABLE t1;", database='test')

    def tearDown(self):
        self.runSql("DROP TABLE t1;", self.master, database='test')
        super(TableCreate,self).tearDown()

class SingleRecordConflict(HealingFixture):
    """Test conflict resolution over single record"""
    def runTest(self):
        self.partition(self.master)
        self.assertSqlSuccess("INSERT INTO t1 VALUES (1, RAND()*100000);", database='test')
        self.unpartition()
        sleep(20)
        self.assertSqlSame("SELECT * FROM t1 ORDER BY c1 DESC;", database='test')
        self.assertSqlEqual("SELECT count(*) AS count FROM t1;", "count\n1\n", database='test')

class NodeStartup(GenieTest):
    """Test heal to node that was shutdown before any updates"""
    def setUp(self):
        if len(self.hosts.hosts) < 2:
            self.skipTest("Insufficient Hosts")
        super(NodeStartup, self).setUp()
        self.master = self.hosts.hosts[0]
        self.slave = self.hosts.hosts[1]
        self.assertSqlSuccess("DROP TABLE IF EXISTS t1;", self.master, database='test')
        self.assertScriptSuccess("/etc/init.d/cloudfabric stop", self.slave)

    def runTest(self):
        self.assertSqlSuccess("CREATE TABLE t1 (c1 INT PRIMARY KEY, c2 INT) ENGINE=GenieDB;", hosts=self.master, database='test')
        self.assertSqlSuccess("INSERT INTO t1 VALUES (1, RAND()*100000), (2, RAND()*100000), (3, RAND()*100000);", hosts=self.master, database='test')
        self.assertSqlSuccess("DELETE FROM t1 WHERE c1=2;", hosts=self.master, database='test')
        self.assertScriptSuccess("/etc/init.d/cloudfabric start", hosts=self.slave)
        sleep(20)
        self.assertSqlSame("SELECT * FROM t1 ORDER BY c1 DESC;", database='test')
        self.assertSqlEqual("SELECT count(*) AS count FROM t1;", "count\n2\n", database='test')

    def tearDown(self):
        self.runSql("DROP TABLE t1;", self.master, database='test')
        super(NodeStartup,self).tearDown()

class NodeStartPartial(HealingFixture):
    """Test heal to node that was shutdown during some updates"""
    def runTest(self):
        self.assertSqlSuccess("INSERT INTO t1 VALUES (1, RAND()*100000), (2, RAND()*100000);", hosts=self.master, database='test')
        self.assertScriptSuccess("/etc/init.d/cloudfabric stop", self.slave)
        self.assertSqlSuccess("INSERT INTO t1 VALUES (3, RAND()*100000);", hosts=self.master, database='test')
        self.assertScriptSuccess("/etc/init.d/cloudfabric start", hosts=self.slave)
        sleep(20)
        self.assertSqlSame("SELECT * FROM t1 ORDER BY c1 DESC;", database='test')
        self.assertSqlEqual("SELECT count(*) AS count FROM t1;", "count\n3\n", database='test')
