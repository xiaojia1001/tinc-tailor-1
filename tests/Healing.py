"""
Tests related to healing.
"""

from tailor.test import GenieTest
from time import sleep
try:
    from unittest.case import expectedFailure
except:
    from unittest2.case import expectedFailure

class SingleRecord(GenieTest):
    """Test conflict resolution over single record"""
    def setUp(self):
        if len(self.hosts.hosts) < 2:
            self.skipTest("Insufficient Hosts")
        super(SingleRecord, self).setUp()
        self.master = self.hosts.hosts[0]
        self.slave = self.hosts.hosts[1]
        self.assertSqlSuccess("DROP TABLE IF EXISTS t1;", self.master, database='test')

    @expectedFailure
    def runTest(self):
        self.assertSqlSuccess("CREATE TABLE t1 (c1 INT PRIMARY KEY, c2 INT) ENGINE=GenieDB;", hosts=self.master, database='test')
        self.partition(self.master)
        self.assertSqlSuccess("INSERT INTO t1 VALUES (1, RAND()*100000);", hosts=self.master, database='test')
        self.unpartition()
        sleep(1)
        self.assertSqlSame("SELECT * FROM t1 ORDER BY c1 DESC;", database='test')
        self.assertSqlEqual("SELECT count(*) AS count FROM t1;", "count\n1\n", database='test')

    def tearDown(self):
        self.runSql("DROP TABLE t1;", self.master, database='test')
        super(SingleRecord,self).tearDown()

class Delete(GenieTest):
    """Test conflict resolution over single record"""
    def setUp(self):
        if len(self.hosts.hosts) < 2:
            self.skipTest("Insufficient Hosts")
        super(Delete, self).setUp()
        self.master = self.hosts.hosts[0]
        self.slave = self.hosts.hosts[1]
        self.assertSqlSuccess("DROP TABLE IF EXISTS t1;", self.master, database='test')

    @expectedFailure
    def runTest(self):
        self.assertSqlSuccess("CREATE TABLE t1 (c1 INT PRIMARY KEY, c2 INT) ENGINE=GenieDB;", hosts=self.master, database='test')
        self.assertSqlSuccess("INSERT INTO t1 VALUES (1, RAND()*100000);", hosts=self.master, database='test')
        self.partition(self.master)
        self.assertSqlSuccess("DELETE FROM t1 WHERE c1=1;", hosts=self.master, database='test')
        self.unpartition()
        sleep(1)
        self.assertSqlSame("SELECT * FROM t1 ORDER BY c1 DESC;", database='test')
        self.assertSqlEqual("SELECT count(*) AS count FROM t1;", "count\n0\n", database='test')

    def tearDown(self):
        self.runSql("DROP TABLE t1;", self.master, database='test')
        super(Delete,self).tearDown()

class TableCreate(GenieTest):
    """Test conflict resolution over single record"""
    def setUp(self):
        if len(self.hosts.hosts) < 2:
            self.skipTest("Insufficient Hosts")
        super(TableCreate, self).setUp()
        self.master = self.hosts.hosts[0]
        self.slave = self.hosts.hosts[1]
        self.assertSqlSuccess("DROP TABLE IF EXISTS t1;", self.master, database='test')

    @expectedFailure
    def runTest(self):
        self.partition(self.master)
        self.assertSqlSuccess("CREATE TABLE t1 (c1 INT PRIMARY KEY, c2 INT) ENGINE=GenieDB;", hosts=self.master, database='test')
        self.assertSqlSuccess("INSERT INTO t1 VALUES (1, RAND()*100000);", hosts=self.master, database='test')
        self.unpartition()
        sleep(1)
        self.assertSqlSame("SHOW CREATE TABLE t1;", database='test')

    def tearDown(self):
        self.runSql("DROP TABLE t1;", self.master, database='test')
        super(TableCreate,self).tearDown()

class SingleRecordConflict(GenieTest):
    """Test conflict resolution over single record"""
    def setUp(self):
        if len(self.hosts.hosts) < 2:
            self.skipTest("Insufficient Hosts")
        super(SingleRecordConflict, self).setUp()
        self.master = self.hosts.hosts[0]
        self.slave = self.hosts.hosts[1]
        self.assertSqlSuccess("DROP TABLE IF EXISTS t1;", self.master, database='test')

    @expectedFailure
    def runTest(self):
        self.assertSqlSuccess("CREATE TABLE t1 (c1 INT PRIMARY KEY, c2 INT) ENGINE=GenieDB;", hosts=self.master, database='test')
        self.partition(self.master)
        self.assertSqlSuccess("INSERT INTO t1 VALUES (1, RAND()*100000);", database='test')
        self.unpartition()
        sleep(1)
        self.assertSqlSame("SELECT * FROM t1 ORDER BY c1 DESC;", database='test')
        self.assertSqlEqual("SELECT count(*) AS count FROM t1;", "count\n1\n", database='test')

    def tearDown(self):
        self.runSql("DROP TABLE t1;", self.master, database='test')
        super(SingleRecordConflict,self).tearDown()
