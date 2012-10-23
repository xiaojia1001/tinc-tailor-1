'''
Created on 26 Sep 2012

@author: david
'''
from tailor import Tailor, Action, AddRepos, UpdateRepos, Upgrade, Install, Try, Command, Uninstall, Rm, PutFile
from logging import DEBUG

class RHChannel(Action):
    def run(self, host):
        if host.properties['distribution'] not in ('redhat, centos'):
            return
        if host.properties['channel'] == 'unstable':
            host.sync_command("sed -e '/unstable/,$ s/enabled=0/enabled=1/' -i /etc/yum.repos.d/GenieDB.repo", root=True)
        else:
            host.sync_command("sed -e '/unstable/,$ s/enabled=1/enabled=0/' -i /etc/yum.repos.d/GenieDB.repo", root=True)

class Cloudfabric(Tailor):
    def install(self, hostnames=[]):
        actions = [
            Try(AddRepos({'debian':['deb http://packages.geniedb.com/debian {channel}/',
                                    'deb http://backports.debian.org/debian-backports squeeze-backports main'],
                          'ubuntu':['deb http://packages.geniedb.com/debian {channel}/',
                                    'deb http://backports.debian.org/debian-backports squeeze-backports main'],
                          'redhat':['http://mirror.bytemark.co.uk/fedora/epel/6/i386/epel-release-6-7.noarch.rpm',
                                    'http://packages.geniedb.com/centos/unstable/geniedb-release-1-2.noarch.rpm'],
                          'centos':['http://mirror.bytemark.co.uk/fedora/epel/6/i386/epel-release-6-7.noarch.rpm',
                                    'http://packages.geniedb.com/centos/unstable/geniedb-release-1-2.noarch.rpm']})),
            Try(RHChannel()),
            Try(UpdateRepos()),
            Try(Install('{cloudfabric_packages}')),
            Try(Command("{service_command} cloudfabric stop", root=True), DEBUG),
            PutFile(self.get_file('cloudfabric.conf'), '/etc/cloudfabric.conf', True),
            Command("{service_command} {mysql_service} start", root=True),
            Try(Command("{install_plugin}", root=True)),
            Command("{service_command} cloudfabric start", root=True),
        ]
        if len(hostnames) is 0:
            hosts = self.hosts
        else:
            hosts = self.hosts.subset(hostnames)
        [hosts.run_action(action) for action in actions]

    def upgrade(self, hostnames=[]):
        actions = [
            Try(UpdateRepos()),
            Try(Upgrade('{cloudfabric_packages}')),
        ]
        if len(hostnames) is 0:
            hosts = self.hosts
        else:
            hosts = self.hosts.subset(hostnames)
        [hosts.run_action(action) for action in actions]

    def remove(self, hostnames=[]):
        actions = [
            Command("{service_command} stop", root=True),
            Uninstall('{cloudfabric_packages}'),
            Try(Rm('/etc/cloudfabric.conf')),
        ]
        if len(hostnames) is 0:
            hosts = self.hosts
        else:
            hosts = self.hosts.subset(hostnames)
        [hosts.run_action(action) for action in actions]
        if len(hostnames) is 0:
            self.hosts.hosts = []
        else:
            self.hosts.filter(hostnames)
    
    def refresh(self):
        actions = [
            PutFile(self.get_file('cloudfabric.conf'), '/etc/cloudfabric.conf', True),
            Command("/etc/init.d/cloudfabric restart", root=True),
        ]
        [self.hosts.run_action(action) for action in actions]
    
    @staticmethod
    def setup_argparse(parser):
        parser.add_argument('--channel','-c', choices=['stable','unstable'], default='unstable', help='Which channel of cloudfabric software to install.')
        subparsers = parser.add_subparsers(title='cloudfabric-command', dest='cloudfabric')
        install_parser = subparsers.add_parser('install', help='install cloudfabric on the given hosts.')
        install_parser.add_argument('install_hosts', type=str, nargs='*')
        upgrade_parser = subparsers.add_parser('upgrade', help='get the lastest version of cloudfabric.')
        upgrade_parser.add_argument('upgrade_hosts', type=str, nargs='*')
        remove_parser = subparsers.add_parser('remove', help='remove cloudfabric from the given hosts.')
        remove_parser.add_argument('remove_hosts', type=str, nargs='*')
        subparsers.add_parser('refresh', help='reload cloudfabric configuration on all hosts.')
    
    def argparse(self, params):
        self.properties['channel']= params.channel
        self.distro_properties['debian'] = {'mysql_service':'mysql', 'install_plugin':'true', 'cloudfabric_packages': 'cloudfabric exampleclient cloudfabric-mysql mysql-server-5.1'}
        self.distro_properties['ubuntu'] = {'mysql_service':'mysql', 'install_plugin':'true', 'cloudfabric_packages': 'cloudfabric exampleclient cloudfabric-mysql mysql-server-5.1'}
        self.distro_properties['redhat'] = {'mysql_service':'mysqld', 'install_plugin':"mysql -e \"INSTALL PLUGIN geniedb SONAME 'ha_geniedb.so';\"", 'cloudfabric_packages': 'cloudfabric cloudfabric-database-adapter cloudfabric-client cloudfabric-mysql mysql-server'}
        self.distro_properties['centos'] = {'mysql_service':'mysqld', 'install_plugin':"mysql -e \"INSTALL PLUGIN geniedb SONAME 'ha_geniedb.so';\"", 'cloudfabric_packages': 'cloudfabric cloudfabric-database-adapter cloudfabric-client cloudfabric-mysql mysql-server'}
        self.params = params
    
    def run(self):
        if self.params.cloudfabric == 'install':
            self.install(self.params.install_hosts)
        elif self.params.cloudfabric == 'upgrade':
            self.upgrade(self.params.upgrade_hosts)
        elif self.params.cloudfabric == 'remove':
            self.remove(self.params.remove_hosts)
        else:
            self.refresh()
