'''
Created on 26 Sep 2012

@author: david
'''
from tailor import Tailor, Command
from argparse import REMAINDER
from logging import DEBUG, getLogger

class Run(Tailor):
    @staticmethod
    def setup_argparse(parser):
        parser.add_argument('command', default=None, nargs=REMAINDER)
    
    def argparse(self, params):
        self.command = params.command
      
    def run(self):
        hostlogger = getLogger('tailor.host')
        hostlogger.setLevel(DEBUG)
        self.hosts.run_action(Command(" ".join(self.command)))