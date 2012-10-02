'''
Created on 26 Sep 2012

@author: david
'''
from tailor import Tailor, Ping

class Check(Tailor):  
    def run(self):
        actions = [Ping(target_host) for target_host in self.hosts]
        [self.hosts.run_action(action) for action in actions]