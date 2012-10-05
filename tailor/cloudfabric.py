'''
Created on 26 Sep 2012

@author: david
'''
from tailor import Tailor, AddRepos, UpdateRepos, Install, Try, Command, Uninstall, Rm, PutFile
from logging import DEBUG

class Cloudfabric(Tailor):
    def install(self, hostnames=[]):
        actions = [
            Try(AddRepos({'debian':['deb http://packages.geniedb.com/debian unstable/',
                                    'deb http://backports.debian.org/debian-backports squeeze-backports main'],
                          'redhat':['http://mirror.bytemark.co.uk/fedora/epel/6/i386/epel-release-6-7.noarch.rpm',
                                    'http://packages.geniedb.com/centos/unstable/geniedb-release-1-2.noarch.rpm'],
                          'centos':['http://mirror.bytemark.co.uk/fedora/epel/6/i386/epel-release-6-7.noarch.rpm',
                                    'http://packages.geniedb.com/centos/unstable/geniedb-release-1-2.noarch.rpm']})),
            Try(UpdateRepos()),
            Try(Install('{cloudfabric_packages}')),
            Try(Command("{service_command} cloudfabric stop"), DEBUG),
            PutFile('cloudfabric.conf', '/etc/cloudfabric.conf', True),
            Try(Command("{install_plugin}")),
            Command("{service_command} cloudfabric start"),
        ]
        if len(hostnames) is 0:
            hosts = self.hosts
        else:
            hosts = self.hosts.subset(hostnames)
        [hosts.run_action(action) for action in actions]
        
    def remove(self, hostnames=[]):
        actions = [
            Command("{service_command} stop"),
            Uninstall('{cloudfabric_packages}'),
            Try(Rm('/etc/cloudfabric.conf')),
        ]
        if len(hostnames) is 0:
            hosts = self.hosts
        else:
            hosts = self.hosts.subset(hostnames)
        [hosts.run_action(action) for action in actions]
    
    def refresh(self):
        actions = [
            Command("/etc/init.d/cloudfabric restart"),
        ]
        [self.hosts.run_action(action) for action in actions]
    
    @staticmethod
    def setup_argparse(parser):
        subparsers = parser.add_subparsers(title='cloudfabric-command', dest='cloudfabric')
        install_parser = subparsers.add_parser('install', help='install cloudfabric on the given hosts.')
        install_parser.add_argument('install_hosts', type=str, nargs='*')
        remove_parser = subparsers.add_parser('remove', help='remove cloudfabric from the given hosts.')
        remove_parser.add_argument('remove_hosts', type=str, nargs='*')
        subparsers.add_parser('refresh', help='reload cloudfabric configuration on all hosts.')
    
    def argparse(self, params):
        self.properties['netname']= params.netname
        self.distro_properties['debian'] = {'install_plugin':'true', 'cloudfabric_packages': 'cloudfabric exampleclient cloudfabric-mysql mysql-server-5.1'}
        self.distro_properties['redhat'] = {'install_plugin':"mysql -e \"INSTALL PLUGIN geniedb SONAME 'ha_geniedb.so';\"", 'cloudfabric_packages': 'cloudfabric cloudfabric-database-adapter cloudfabric-client cloudfabric-mysql mysql-server'}
        self.distro_properties['centos'] = {'install_plugin':"mysql -e \"INSTALL PLUGIN geniedb SONAME 'ha_geniedb.so';\"", 'cloudfabric_packages': 'cloudfabric cloudfabric-database-adapter cloudfabric-client cloudfabric-mysql mysql-server'}
        self.params = params
    
    def run(self):
        if self.params.cloudfabric == 'install':
            self.install(self.params.install_hosts)
        elif self.params.cloudfabric == 'remove':
            self.remove(self.params.remove_hosts)
        else:
            self.refresh()
