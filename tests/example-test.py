"""Long documentation for test suite!"""

from tailor.test import Test

class ExTest(Test):
    """Long documentation for test!"""
    
    def run(self):
        self.logger.info('3')

class SkippedTest(Test):
    def setUp(self):
        self.require(False)

class Fixture(Test):
    def setUp(self):
        self.require(len(self.hosts.hosts) >= 2)
        self.master = self.hosts.hosts[0]
        self.slave = self.hosts.hosts[1]
    
    def tearDown(self):
        pass

class ExamplePass(Fixture):
    def run(self):
        self.expect(self.master.sync_command('hostname')==0)

class ExampleException(Fixture):
    def run(self):
        raise Exception()

class ExampleFailure(Fixture):
    def run(self):
        self.expect(False)

class ExampleAssert(Fixture):
    def run(self):
        assert(False)

test=[ExTest,SkippedTest,ExamplePass,ExampleException,ExampleFailure,ExampleAssert]