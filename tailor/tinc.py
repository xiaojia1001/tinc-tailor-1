'''
Created on 26 Sep 2012

@author: david
'''
from tailor import *
from logging import DEBUG, INFO
from errno import ENOENT

class Tinc(Tailor):
    def install(self, hostnames=None):
        actions = [
            Try(Preinstall()),
            Try(Install('{tinc_package}')),
            Try(Mkdir('/etc/tinc/'), DEBUG),
            Mkdir('/etc/tinc/{netname}'),
            Mkdir('/etc/tinc/{netname}/hosts'),
            PutFile('nets.boot', '/etc/tinc/nets.boot', True),
            PutFile('tinc.conf', '/etc/tinc/{netname}/tinc.conf', True),
            PutFile('host.conf', '/etc/tinc/{netname}/hosts/{hostname}', True),
            Command("tincd -n {netname} -K4096"),
            GetFile('/etc/tinc/cf/hosts/{hostname}', 'hosts/{hostname}')
        ]
        if hostnames is None:
            hosts = self.hosts
        else:
            hosts = self.hosts.subset(hostnames)
        [hosts.run_action(action) for action in actions]
        
    def remove(self, hostnames=None):
        actions = [
            Uninstall('{tinc_package}'),
            Try(Rmdir('/etc/tinc/{netname}')),
            Try(Rm('/etc/tinc/nets.boot')),
            Command("! pgrep -f '^tincd -n {netname}' || pkill -9 -f '^tincd -n {netname}'"),
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
            PutFile('tinc.conf', '/etc/tinc/{netname}/tinc.conf', True),
            PutDir('hosts/', '/etc/tinc/{netname}/hosts/'),
            Command('pkill -SIGHUP -f "^tincd -n {netname}" || tincd -n {netname}'),
            Try(Command('ip addr flush {netname} '), INFO),
            Command('ip addr add {private_ipv4_cidr} dev {netname}'),
            Command('ip link set {netname} up')
        ]
        [self.hosts.run_action(action) for action in actions]
    
    @staticmethod
    def setup_argparse(parser):
        subparsers = parser.add_subparsers(title='tinc-command', dest='tinc')
        install_parser = subparsers.add_parser('install', help='install tinc on the given hosts.')
        install_parser.add_argument('hosts', type=str, nargs='+')
        remove_parser = subparsers.add_parser('remove', help='remove tinc from the given hosts.')
        remove_parser.add_argument('hosts', type=str, nargs='+')
        refresh_parser = subparsers.add_parser('refresh', help='reload tinc configuration on all hosts.')
    
    def argparse(self, params):
        self.properties['netname']= params.netname
        self.properties['tinc_package'] = 'tinc'
        self.params = params
    
    def run(self):
        if self.params.tinc == 'install':
            self.install(self.params.hosts)
        elif self.params.tinc == 'remove':
            self.remove(self.params.hosts)
        self.refresh()