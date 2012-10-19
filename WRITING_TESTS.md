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

* **assertSqlSuccess(*query*, *hosts*=None, *database*="")**

  This function runs the SQL query *query* on several hosts, and asserts that
  no error occurs. If *hosts* is unspecified, the query is run on all known
  hosts, otherwise it can point to a Host object or list of Host objects.

* **assertSqlFailure(*query*, *hosts*=None, *database*="")**

  This function does exactly as assertSqlSuccess, except that it asserts that
  an error does occur.

* **assertSqlSame(*query*, *hosts*=None, *database*="", *force*=False)**

  This function operates as assertSqlSuccess, except that it additionally
  checks that all the hosts returned the same result. If *force*=True is given
  then no assertion occurs on Sql failure, but the result is still checked.

* **assertSqlEqual(*query*, *expected*, *hosts*=None, *database*, *force*=False)**

  This function operates as assertSqlSame, except that it additionally checks
  that the output returned by the hosts matches *expected*.

* **assertScriptSuccess(*script*, *hosts*=None)**

  This function executes the shell script given by *script* on several hosts,
  and asserts that the script returns code 0. *hosts* is interpreted as with
  the above functions.

* **assertScriptSame(*script*, *hosts*)**

  This function operates as assertScriptSuccess, except that it additionally
  checks that all the hosts return the same result.

* **assertScriptEqual(*script*, *expected*, *hosts*)**

  This function operates as assertScriptSame, except that it additionally
  checks that the output returned by the hosts matches *expected*.

`GenieTest` also provides several functions that are *not* assertions, but
are vital in constucting powerful tests:

* **runSql(*query*, *host*=None, *database*="", *force*=False)**

  This function runs the SQL statements *query* on the given *host*. If *host*
  is not given, it defaults to the first host. If *force*=True, execution does
  not stop if a statment has an error.

  This function returns a tuple of the sql result and a return code (0 for
  success).

* **runScript(*script*, *host*=None)**

  This function runs the shell script *script* on the given *host*. If *host*
  is not given, it defaults to the first host.

  This function returns a tuple of the script output and return code.

* **partition(*partitioned_hosts*)**

  This function introduces a network split between the hosts in
  *partitioned_hosts* and those not in it (the split is symetric). A single
  Host or a list of Hosts may be given.

  Only one partition at a time is allowed.

* **unpartition()**

  This function restores any previously introduced partition. This function
  is automatically called on tearDown().

* **setHostDelay(*hosts*=None, *delay*=100)**

  This function makes all network data sent from *hosts* (which may be None,
  for all hosts, a particular Host or a list of hosts) delayed by *delay*
  milliseconds before going over the network.

  The same host may have setHostDelay called several times, and the last value
  will be used.

* **clearHostDelay(*hosts*=None)**

  This function removes any network delay introduced by setHostDelay. *hosts*
  may be None, in which case all hosts have their delay cleared, or a Host
  object or a list of Host objects. This function is automatically called on
  tearDown().
