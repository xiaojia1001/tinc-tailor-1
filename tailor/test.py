'''
Created on 2 Oct 2012

@author: david
'''

from sys import path
from time import time
from itertools import chain
from traceback import print_exception
from logging import getLogger, INFO
try:
    from unittest import TestCase, defaultTestLoader, TestResult
    from unittest.result import failfast
except:
    from unittest2 import TestCase, defaultTestLoader, TestResult
    from unittest2.result import failfast
from tailor import Tailor, Host, can_color
from argparse import FileType

path.append('tests')

if can_color():
    NORMAL='\x1b[0m'
else:
    NORMAL=''

class MultiTestResult(TestResult):
    def __init__(self, results, *args, **kwargs):
        super(MultiTestResult, self).__init__(*args, **kwargs)
        self.results=results
        self.dispatch("startTestRun")
        self.dispatch("startTest")
        self.dispatch("stopTestRun")
        self.dispatch("stopTest")
        self.dispatch("endTestRun")
        self.dispatch("endTest")
        self.dispatch("addError")
        self.dispatch("addFailure")
        self.dispatch("addSuccess")
        self.dispatch("addSkip")
        self.dispatch("addExpectedFailure")
        self.dispatch("addUnexpectedSuccess")

    def dispatch(self, name):
        def fn(*args, **kwargs):
            for res in self.results:
                result = getattr(res, name)(*args, **kwargs)
            return result
        setattr(self,name,fn)

class TailorTestResult(TestResult):
    def __init__(self, logger, *args, **kwargs):
        super(TailorTestResult, self).__init__(*args, **kwargs)
        self.logger = logger
        self.testsRunThisModule = 0
        self.modulesRun = 0
        self.lastModule = None

    def startTestRun(self):
        TestResult.startTestRun(self)
        self.startRunTime = time()

    def stopTestRun(self):
        super(TailorTestResult, self).stopTestRun()
        if self.lastModule is not None:
            self.logger.info("[----------]"+NORMAL+" %d tests from %s (%d ms total)", self.testsRunThisModule, self.lastModule, (time()-self.startModuleTime)*1000)
            self.logger.info(" ")
        self.logger.info("[----------]"+NORMAL+" Global test environment tear-down")
        self.logger.info("[==========]"+NORMAL+" %d tests from %d test cases ran. (%d ms total)", self.testsRun, self.modulesRun, (time()-self.startRunTime)*1000)
        self.logger.info("[  PASSED  ]"+NORMAL+" %d tests.", self.testsRun - len(self.failures) - len(self.errors) - len(self.skipped) - len(self.unexpectedSuccesses))

        if len(self.failures) + len(self.errors) + len(self.unexpectedSuccesses) > 0:
            self.logger.error("[  FAILED  ]"+NORMAL+" %s test, listed below:", len(self.failures) + len(self.errors) + len(self.unexpectedSuccesses))
        for failure in chain(self.failures, self.errors, self.unexpectedSuccesses):
            self.logger.error("[  FAILED  ]"+NORMAL+" %s", failure[0].id())

    def startTest(self, test):
        super(TailorTestResult, self).startTest(self)
        if self.lastModule is not test.__class__.__module__:
            if self.lastModule is not None:
                self.logger.info("[----------]"+NORMAL+" %d tests from %s (%d ms total)", self.testsRunThisModule, self.lastModule, (time()-self.startModuleTime)*1000)
                self.logger.info(" ")
            self.lastModule = test.__class__.__module__
            self.testsRunThisModule = 0
            self.modulesRun += 1
            self.logger.info("[----------]"+NORMAL+" %s", self.lastModule)
            self.startModuleTime = time()

        self.testsRunThisModule += 1
        self.logger.info("[ RUN      ]"+NORMAL+" %s", test.id())
        self.logger.debug("[ INFO     ] %s", test.__doc__)
        self.startTestTime = time()

    @failfast
    def addError(self, test, err):
        super(TailorTestResult, self).addError(test,err)
        print_exception(err[0], err[1], err[2])
        self.logger.error("[    ERROR ]"+NORMAL+" %s (%d ms)", test.id(), (time()-self.startTestTime)*1000)

    @failfast
    def addFailure(self, test, err):
        super(TailorTestResult, self).addFailure(test,err)
        print_exception(err[0], err[1], err[2])
        self.logger.error("[   FAILED ]"+NORMAL+" %s (%d ms)", test.id(), (time()-self.startTestTime)*1000)

    def addSuccess(self, test):
        super(TailorTestResult, self).addSuccess(test)
        self.logger.info("[       OK ]"+NORMAL+" %s (%d ms)", test.id(), (time()-self.startTestTime)*1000)

    def addSkip(self, test, reason):
        super(TailorTestResult, self).addSkip(test,reason)
        self.logger.warning("[ SKIPPING ]"+NORMAL+" " + reason)

    def addExpectedFailure(self, test, err):
        super(TailorTestResult, self).addExpectedFailure(test,err)
        self.logger.info("[       OK ]"+NORMAL+" %s (%d ms)", test.id(), (time()-self.startTestTime)*1000)

    @failfast
    def addUnexpectedSuccess(self, test):
        super(TailorTestResult, self).addUnexpectedSuccess(test)
        self.logger.error("Expected Failure")
        self.logger.error("[   FAILED ]"+NORMAL+" %s (%d ms)", test.id(), (time()-self.startTestTime)*1000)

class TestRunner(Tailor):
    def __init__(self, *args, **kwargs):
        super(TestRunner, self).__init__(*args, **kwargs)
        self.logger = getLogger('tailor.test.runner')
        
    def run_test(self, test):
        result = TailorTestResult(self.logger)
        if self.params.xml is not None:
            from junitxml import JUnitXmlResult
            result = MultiTestResult([result,JUnitXmlResult(self.params.xml)])
        startTestRun = getattr(result, 'startTestRun', None)
        if startTestRun is not None:
            startTestRun()
        try:
            test(result)
        finally:
            stopTestRun = getattr(result, 'stopTestRun', None)
            if stopTestRun is not None:
                stopTestRun()
    
    def run(self):
        if not self.logger.isEnabledFor(INFO):
            self.logger.setLevel(INFO)
        Test.hosts = self.hosts
        if len(self.params.tests) is 0:
            tests = defaultTestLoader.discover('tests', '*.py')
        else:
            tests = defaultTestLoader.loadTestsFromNames(self.params.tests)

        self.run_test(tests)
        
    @staticmethod
    def setup_argparse(parser):
        parser.add_argument('--xml', type=FileType(mode='w'))
        parser.add_argument('tests', type=str, nargs='*')

class Test(TestCase):
    def __init__(self,  *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)
        self.logger = getLogger('tailor.test.'+self.__class__.__name__)
        self.addTypeEqualityFunc(str, 'assertMultiLineEqual')
        self.maxDiff = None
    
    def __enter__(self):
        self.setUp()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.tearDown()

    def runSql(self, query, host=None, database="", password=None, force=False):
        if host is None:
            host = self.hosts.hosts[0]
        if force:
            force = "-f"
        else:
            force = ""
        if password is not None:
            password = '-p'+password
        elif host.properties.has_key('mysql_password'):
            password = "-p"+host.properties['mysql_password']
        else:
            password = ""
        host.logger.debug('Running SQL:\n'+query)
        chan = host.async_command("mysql {force} {password} {database}".format(database=database, password=password, force=force))
        chan.sendall(query)
        chan.shutdown_write()
        result = "".join(chan.makefile())
        host.logger.debug(result)
        chan.recv_exit_status()
        return (result, chan.exit_status)

    def assertSqlSuccess(self, query, hosts=None, *args, **kwargs):
        if hosts is None:
            hosts = self.hosts
        if isinstance(hosts, Host):
            hosts = [hosts]
        for host in hosts:
            result, status = self.runSql(query, host, *args, **kwargs)
            self.assertEqual(0, status, "Query Failed.\nHost: {0}\nQuery: {1}\nResult: {2}".format(host.hostname, query, result))
        return result

    def assertSqlFailure(self, query, hosts=None, *args, **kwargs):
        if hosts is None:
            hosts = self.hosts
        if isinstance(hosts, Host):
            hosts = [hosts]
        for host in hosts:
            result, status = self.runSql(query, host, *args, **kwargs)
            self.assertNotEqual(0, status, "Query Succeeded for some reason.\nHost: {0}\nQuery: {1}\nResult: {2}".format(host.hostname, query, result))
        return result

    def runScript(self, script, host=None):
        if host is None:
            host = self.hosts.hosts[0]
        host.logger.debug('Running script:\n'+script)
        chan = host.async_command('sh')
        chan.sendall(script)
        chan.shutdown_write()
        result = "".join(chan.makefile())
        host.logger.debug(result)
        chan.recv_exit_status()
        return (result, chan.exit_status)

    def assertScriptSuccess(self, script, hosts=None, *args, **kwargs):
        if hosts is None:
            hosts = self.hosts
        if isinstance(hosts, Host):
            hosts = [hosts]
        for host in hosts:
            result, status = self.runScript(script, host, *args, **kwargs)
            self.assertEqual(0, status, "Script failed.\nHost: {0}\nScript: {1}\nResult: {2}".format(host.hostname,script, result))
        return result

    def assertSqlEqual(self, query, desiredResult, hosts=None, msg=None, *args, **kwargs):
        if hosts is None:
            hosts = self.hosts
        for host in hosts:
            self.assertEqual(desiredResult, self.assertSqlSuccess(query, host, *args, **kwargs), msg)

    def assertSqlSame(self, query, hosts=None, msg=None, *args, **kwargs):
        result = None
        if hosts is None:
            hosts = self.hosts
        for host in hosts:
            thisResult = self.assertSqlSuccess(query, host, *args, **kwargs)
            if result is None:
                result = thisResult
            else:
                self.assertEqual(result, thisResult, msg)

    def assertScriptEqual(self, script, desiredResult, hosts=None, msg=None):
        if hosts is None:
            hosts = self.hosts
        for host in hosts:
            self.assertEqual(desiredResult, self.assertScriptSuccess(script, host), msg)

    def assertScriptSame(self, script, hosts=None, msg=None):
        result = None
        if hosts is None:
            hosts = self.hosts
        for host in hosts:
            thisResult = self.assertScriptSuccess(script, host)
            if result is None:
                result = thisResult
            else:
                self.assertEqual(result, thisResult, msg)

class GenieTest(Test):
    def setUp(self):
        super(GenieTest,self).setUp()
        self.assertScriptSuccess("""
        /etc/init.d/mysql* stop
        /etc/init.d/cloudfabric stop
        rm -rf /var/log/{cloudfabric-core,DatabaseAdapter}.{log,trace} /var/lib/cloudfabric/* /dev/shm/CloudFabric /var/run/cloudfabric.stats
        truncate --size=0 /var/log/geniedb_se.log
        """)
        self.assertScriptSuccess("""
        /etc/init.d/cloudfabric start
        /etc/init.d/mysql* start
        """)

    def tearDown(self):
        self.assertScriptSuccess("""
        java -cp /usr/share/java/DatabaseAdapter.jar com.sleepycat.je.util.DbDump -h /var/lib/cloudfabric -l | grep '[^$].\$$' | cut -d . -f 1 | xargs -I{} echo rm -rf /var/lib/mysql/{}
        """)
        super(GenieTest,self).tearDown()
