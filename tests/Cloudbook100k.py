#!/usr/bin/env python


from tailor.test import GenieTest
from os import path

class Cloudbook100k(GenieTest):
    """Test we can load replicate cloudbook fully"""
    def setUp(self):
        super(Cloudbook100k, self).setUp()
        if len(self.hosts.hosts) < 2:
            self.skipTest("Insufficient Hosts")
        try:
            self.sqlLoad = "".join(open(path.join(path.abspath(path.dirname(__file__)), 'gdb_JustCloudboo_cl.sql')).readlines())
        except:
            self.skipTest("Could not find sql data")
        self.master = self.hosts.hosts[0]
        self.slave = self.hosts.hosts[1]

    def runTest(self):
        self.assertSqlSuccess("DROP DATABASE geniedb_cl;", hosts=self.master, password='geniedb2012', force=True)
        self.assertSqlSuccess("CREATE DATABASE geniedb_cl;", hosts=self.master, password='geniedb2012')
        self.assertSqlSuccess(self.sqlLoad, hosts=self.slave, password='geniedb2012')
        self.assertScriptSame('for i in `mysql -Ns -pgeniedb2012 -e "show tables in geniedb_cl;"`; do   echo $i `mysql -Ns -pgeniedb2012 -e "select count(*) from geniedb_cl.$i;"`; done')
