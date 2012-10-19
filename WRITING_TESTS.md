Writing multi-node cloudfabric tests
====================================

Each test is a `python` class deriving from tailor.test.GenieTest. This class
is a standard python `unittest.TestCase`, so the [standard documentation
applies](http://docs.python.org/library/unittest.html). A good template to
start from is:

    class YourTest(GenieTest):
        """One line explaining what your test does!"""
        def setUp(self):
            if len(self.hosts.hosts) < 2:
                self.skipTest("Insufficient Hosts")
            super(YourTest, self).setUp()
            self.master = self.hosts.hosts[0]
            self.slave = self.hosts.hosts[1]
            self.assertSqlSuccess("DROP TABLE IF EXISTS t1;", self.master, database='test')

        def runTest(self):
            self.assertSqlSuccess("CREATE TABLE t1 (c1 INT AUTO_INCREMENT PRIMARY KEY, c2 INT) ENGINE=GenieDB;", hosts=self.master, database='test')

        def tearDown(self):
            self.runSql("DROP TABLE t1;", self.master, database='test')
            super(YourTest,self).tearDown()

This provides a few common features:

* It ensure the test is run with at least two hosts
* It sets up `self.master` and `self.slave` as aliases we can use to refer to
  particular hosts. This is useful as some commands, like `CREATE TABLE` should
  only be run on one host.
* It provides an example of creating a table, including how we must ensure in
  the `setUp` that the table doesn't already exist, and cleaning up in the
  tearDown.


Like any `python unittest` test, we write the body of the test in the `runTest`
function.  The actual testing is done by calling assertion functions. In
addition to the usual `python` assertions such as `assertEqual` and
`assertTrue`, `GenieTest` provides:

* **assertSqlSuccess**
* **assertSqlFailure**
* **assertSqlSame**
* **assertSqlEqual**
* **assertScriptSuccess**
* **assertScriptEqual**
* **assertScriptSame**

`GenieTest` also provides several functions that are *not* assertions, but
are vital in constucting powerful tests:

* **runSql**
* **runScript**
* **partition**
* **unpartition**
* **setHostDelay**
* **clearHostDelay**
