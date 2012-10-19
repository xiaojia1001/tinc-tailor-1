'''
Created on 26 Sep 2012

@author: david
'''
from tailor import Tailor, Try, AddRepos, UpdateRepos, Install, Mkdir, PutFile, Command, GetFile, Uninstall, Rmdir, Rm, PutDir
from os import remove
from logging import DEBUG, INFO
from errno import ENOENT

class Tinc(Tailor):
    def install(self, hostnames=[]):
        actions = [
            Try(AddRepos({'redhat':'http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.2-2.el6.rf.x86_64.rpm',
                          'centos':'http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.2-2.el6.rf.x86_64.rpm'})),
            Try(UpdateRepos()),
            Try(Install('{tinc_package}')),
            Try(Mkdir('/etc/tinc/'), DEBUG),
            Mkdir('/etc/tinc/{netname}'),
            Mkdir('/etc/tinc/{netname}/hosts'),
            PutFile(self.get_file('nets.boot'), '/etc/tinc/nets.boot', True),
            PutFile(self.get_file('tinc.conf'), '/etc/tinc/{netname}/tinc.conf', True),
            PutFile(self.get_file('host.conf'), '/etc/tinc/{netname}/hosts/{hostname}', True),
            Command("tincd -n {netname} -K4096"),
            GetFile('/etc/tinc/cf/hosts/{hostname}', 'hosts/{hostname}')
        ]
        if len(hostnames) is 0:
            hosts = self.hosts
        else:
            hosts = self.hosts.subset(hostnames)
        [hosts.run_action(action) for action in actions]
        
    def remove(self, hostnames=[]):
        actions = [
            Uninstall('{tinc_package}'),
            Try(Rmdir('/etc/tinc/{netname}')),
            Try(Rm('/etc/tinc/nets.boot')),
            Command("! pgrep -f '^tincd -n {netname}' || pkill -9 -f '^tincd -n {netname}'"),
        ]
        if len(hostnames) is 0:
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
        if len(hostnames) is 0:
            self.hosts.hosts = []
        else:
            self.hosts.filter(hostnames)
    
    def refresh(self):
        actions = [
            PutFile(self.get_file('tinc.conf'), '/etc/tinc/{netname}/tinc.conf', True),
            PutDir('hosts/', '/etc/tinc/{netname}/hosts/'),
            Command('pkill -SIGHUP -f "^((/usr)?/s?bin/)?tincd -n {netname}" || tincd -n {netname}'),
            Try(Command('ip addr flush {netname} '), INFO),
            Command('ip addr add {private_ipv4_cidr} dev {netname}'),
            Command('ip link set {netname} up')
        ]
        [self.hosts.run_action(action) for action in actions]
    
    @staticmethod
    def setup_argparse(parser):
        subparsers = parser.add_subparsers(title='tinc-command', dest='tinc')
        install_parser = subparsers.add_parser('install', help='install tinc on the given hosts.')
        install_parser.add_argument('install_hosts', type=str, nargs='*')
        remove_parser = subparsers.add_parser('remove', help='remove tinc from the given hosts.')
        remove_parser.add_argument('remove_hosts', type=str, nargs='*')
        subparsers.add_parser('refresh', help='reload tinc configuration on all hosts.')
    
    def argparse(self, params):
        self.properties['tinc_package'] = 'tinc'
        self.params = params
    
    def run(self):
        if self.params.tinc == 'install':
            self.install(self.params.install_hosts)
        elif self.params.tinc == 'remove':
            self.remove(self.params.remove_hosts)
        self.refresh()