"""
Tests for issues in JIRA.
"""

from tailor.test import GenieTest
from os import path
from time import sleep
try:
    from unittest.case import expectedFailure
except:
    from unittest2.case import expectedFailure

class GDB379(GenieTest):
    """Test we can load wordpress data on one node, then run a query on the other"""
    def setUp(self):
        if len(self.hosts.hosts) < 2:
            self.skipTest("Insufficient Hosts")
        try:
            self.sqlLoad = "".join(open(path.join(path.abspath(path.dirname(__file__)), 'wordpress.sql')).readlines())
        except:
            self.skipTest("Could not find sql data")
        super(GDB379, self).setUp()
        self.master = self.hosts.hosts[0]
        self.slave = self.hosts.hosts[1]
    
    def runTest(self):
        self.assertSqlSuccess(self.sqlLoad, hosts=self.master, force=True)
        sleep(10)
        self.assertSqlSuccess("SELECT SQL_CALC_FOUND_ROWS wp_posts.ID FROM wp_posts WHERE 1=1 AND wp_posts.post_type = 'post' AND (wp_posts.post_status = 'publish') ORDER BY wp_posts.post_date DESC LIMIT 0, 10;", hosts=self.slave, database='wp_test')

class GDB402(GenieTest):
    """Test we can load replicate cloudbook fully"""
    def setUp(self):
        if len(self.hosts.hosts) < 2:
            self.skipTest("Insufficient Hosts")
        try:
            self.sqlLoad = "".join(open(path.join(path.abspath(path.dirname(__file__)), 'gdb_JustCloudboo_cl.sql')).readlines())
        except:
            self.skipTest("Could not find sql data")
        super(GDB402, self).setUp()
        self.master = self.hosts.hosts[0]
        self.slave = self.hosts.hosts[1]

    @expectedFailure
    def runTest(self):
        self.assertSqlSuccess("DROP DATABASE geniedb_cl;", hosts=self.master, force=True)
        self.assertSqlSuccess("CREATE DATABASE geniedb_cl;", hosts=self.master)
        sleep(1)
        self.assertSqlSuccess(self.sqlLoad, hosts=self.slave)
        sleep(10)
        self.assertScriptSame('for i in `mysql -Ns -pgeniedb2012 -e "show tables in geniedb_cl;"`; do   echo $i `mysql -Ns -pgeniedb2012 -e "select count(*) from geniedb_cl.$i;"`; done')
