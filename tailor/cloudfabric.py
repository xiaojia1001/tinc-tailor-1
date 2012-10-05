'''
Created on 26 Sep 2012

@author: david
'''
from tailor import *
from logging import DEBUG
from errno import ENOENT

class Cloudfabric(Tailor):
    def install(self, hostnames=None):
        actions = [
            Try(AddRepos({'debian':['deb http://packages.geniedb.com/debian unstable/',
                                    'deb http://backports.debian.org/debian-backports squeeze-backports main'],
                          'redhat':['http://mirror.bytemark.co.uk/fedora/epel/6/i386/epel-release-6-7.noarch.rpm',
                                    'http://packages.geniedb.com/centos/unstable/geniedb-release-1-1.noarch.rpm'],
                          'centos':['http://mirror.bytemark.co.uk/fedora/epel/6/i386/epel-release-6-7.noarch.rpm',
                                    'http://packages.geniedb.com/centos/unstable/geniedb-release-1-1.noarch.rpm']})),
            Try(Install('cloudfabric-mysql')),
            Try(Command("/etc/init.d/cloudfabric stop"), DEBUG),
            PutFile('cloudfabric.conf', '/etc/cloudfabric.conf', True),
            Command("/etc/init.d/cloudfabric start"),
        ]
        if hostnames is None:
            hosts = self.hosts
        else:
            hosts = self.hosts.subset(hostnames)
        [hosts.run_action(action) for action in actions]
        
    def remove(self, hostnames=None):
        actions = [
            Command("/etc/init.d/cloudfabric stop"),
            Uninstall('cloudfabric-mysql'),
            Try(Rm('/etc/cloudfabric.conf')),
        ]
        if hostnames is None:
            hosts = self.hosts
        else:
            hosts = self.hosts.subset(hostnames)
        for host in hosts:
            try:
                remove(host.interpolate('hosts/{hostname}'))
            except OSError as e:
                if e.errno is not ENOENT:
                    raise
        [hosts.run_action(action) for action in actions]
        if hostnames is None:
            self.hosts.hosts = []
        else:
            self.hosts.filter(hostnames)
    
    def refresh(self):
        actions = [
            Command("/etc/init.d/cloudfabric restart"),
        ]
        [self.hosts.run_action(action) for action in actions]
    
    @staticmethod
    def setup_argparse(parser):
        subparsers = parser.add_subparsers(title='cloudfabric-command', dest='cloudfabric')
        install_parser = subparsers.add_parser('install', help='install cloudfabric on the given hosts.')
        install_parser.add_argument('install_hosts', type=str, nargs='+')
        remove_parser = subparsers.add_parser('remove', help='remove cloudfabric from the given hosts.')
        remove_parser.add_argument('remove_hosts', type=str, nargs='+')
        refresh_parser = subparsers.add_parser('refresh', help='reload cloudfabric configuration on all hosts.')
    
    def argparse(self, params):
        self.properties['netname']= params.netname
        self.params = params
    
    def run(self):
        if self.params.cloudfabric == 'install':
            self.install(self.params.install_hosts)
        elif self.params.cloudfabric == 'remove':
            self.remove(self.params.remove_hosts)
        else:
            self.refresh()
