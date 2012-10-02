'''
Created on 2 Oct 2012

@author: david
'''

from tailor import Tailor
from sys import path, stderr
from logging import getLogger, INFO
from traceback import print_exc, extract_stack, format_list

path.append('tests')

class TestRunner(Tailor):
    def __init__(self, *args, **kwargs):
        super(TestRunner, self).__init__(*args, **kwargs)
        self.logger = getLogger('tailor.test.runner')
        
    def run_suite(self, testname):
        module = __import__(testname)
        self.logger.info("[----------] " + testname)
        if module.__doc__ is not None:
            self.logger.debug(module.__doc__)
        for testClass in module.test:
            self.logger.info("[ RUN      ] " + testClass.__name__)
            if testClass.__doc__ is not None:
                self.logger.debug(testClass.__doc__)
            try:
                with testClass(self.hosts) as a:
                    a.run()
            except UnsatisfiedRequirement:
                self.logger.warning("[ SKIPPING ]")
            except AssertionError as e:
                print_exc()
                self.logger.error("[   FAILED ]")
            except:
                print_exc()
                self.logger.error("[   FAILED ]")
            else:
                self.logger.info("[       OK ]")
        self.logger.info("[----------] ")
    
    def run(self):
        [self.run_suite(testname) for testname in self.params.tests]
        
    @staticmethod
    def setup_argparse(parser):
        parser.add_argument('tests', type=str, nargs='+')
    
    def argparse(self, params):
        self.properties['netname']= params.netname
        self.params = params
        getLogger('tailor.test.runner').setLevel(INFO)

class UnsatisfiedRequirement(Exception):
    pass

class Test(object):
    def __init__(self, hosts):
        self.hosts = hosts
        self.logger = getLogger('tailor.test.'+self.__class__.__name__)
    
    def __enter__(self):
        self.setUp()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.tearDown()
    
    def setUp(self):
        pass
    
    def run(self):
        pass
    
    def tearDown(self):
        pass
    
    def expect(self, passed, msg="Expectation failed"):
        if passed == False:
            for line in format_list(x for x in extract_stack() if not x[0].endswith('/test.py') and not x[0].endswith('/tinc-tailor')):
                stderr.write(line)
            self.logger.error(msg)
    
    def require(self, passed, msg="Requirement failed"):
        if passed == False:
            raise UnsatisfiedRequirement(msg)
