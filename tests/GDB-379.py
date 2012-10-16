from tailor.test import GenieTest

class GDB379(GenieTest):
    """Test we can load wordpress data on one node, then run a query on the other"""
    def setUp(self):
        super(GDB379, self).setUp()
        if len(self.hosts.hosts) < 2:
            self.skipTest("Insufficient Hosts")
        try:
            self.sqlLoad = "".join(open(path.join(path.abspath(path.dirname(__file__)), 'wordpress.sql')).readlines())
        except:
            self.skipTest("Could not find sql data")
        self.master = self.hosts.hosts[0]
        self.slave = self.hosts.hosts[1]
    
    def runTest(self):
        self.assertSqlSuccess(self.sqlLoad, hosts=self.master, force=True)
        self.assertSqlSuccess("SELECT SQL_CALC_FOUND_ROWS wp_posts.ID FROM wp_posts WHERE 1=1 AND wp_posts.post_type = 'post' AND (wp_posts.post_status = 'publish') ORDER BY wp_posts.post_date DESC LIMIT 0, 10;", hosts=self.slave, database='wp_test')
