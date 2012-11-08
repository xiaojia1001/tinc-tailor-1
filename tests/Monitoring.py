"""
Test status monitoring tools.
"""

from tailor.test import GenieTest
from socket import gethostbyname
from json import loads
from time import sleep
try:
    from unittest.case import expectedFailure
except:
    from unittest2.case import expectedFailure

class All(GenieTest):
    """Test status reporting with all nodes connected."""
    def runTest(self):
        sleep(2)
        for controlHost in self.hosts:
            done_nids=[]
            result, status = self.runScript("monitor", controlHost, False)
            self.assertEqual(0, status)
            data = loads(result)
            self.assertEqual(len(self.hosts), len(data))
            for reportedHost in data:
                host = None
                for localHost in self.hosts:
                    if localHost.properties['number'] == str(reportedHost['nid']):
                        host = localHost
                        break
                self.assertIsNotNone(host, "Monitor reported a host we could not find")
                self.assertNotIn(reportedHost['nid'], done_nids, "Monitor reported host %s twice" % reportedHost['nid'])
                done_nids.append(reportedHost['nid'])
                self.assertEqual(reportedHost['ip'], host.properties['application_address'])
                self.assertEqual(reportedHost['cid'], 1)
                self.assertEqual(str(reportedHost['nid']), host.properties['number'])
                self.assertEqual(reportedHost['state'], "CONNECTED")
                self.assertIn('lastSeen', reportedHost)
                self.assertIn('lastReported', reportedHost)
                self.assertIn('lastReportedLocal', reportedHost)

class Partitioned(GenieTest):
    """Test status reporting with a partition."""
    def setUp(self):
        if len(self.hosts.hosts) < 2:
            self.skipTest("Insufficient Hosts")
        super(Partitioned, self).setUp()
        self.master = self.hosts.hosts[0]

    def runTest(self):
        sleep(2)
        for controlHost in self.hosts:
            result, status = self.runScript("monitor", controlHost, False)
        self.partition(self.master)
        sleep(3)
        for controlHost in self.hosts:
            done_nids=[]
            result, status = self.runScript("monitor", controlHost, False)
            self.assertEqual(0, status)
            data = loads(result)
            self.assertEqual(len(self.hosts), len(data))
            for reportedHost in data:
                host = None
                for localHost in self.hosts:
                    if localHost.properties['number'] == str(reportedHost['nid']):
                        host = localHost
                        break
                self.assertIsNotNone(host, "Monitor reported a host we could not find")
                self.assertNotIn(reportedHost['nid'], done_nids, "Monitor reported host %s twice" % reportedHost['nid'])
                done_nids.append(reportedHost['nid'])
                self.assertEqual(reportedHost['ip'], host.properties['application_address'])
                self.assertEqual(reportedHost['cid'], 1)
                self.assertEqual(str(reportedHost['nid']), host.properties['number'])
                if (controlHost is self.master and host is self.master) or \
                   (controlHost is not self.master and host is not self.master):
                    self.assertEqual(reportedHost['state'], "CONNECTED")
                else:
                    self.assertEqual(reportedHost['state'], "DISCONNECTED")
                self.assertIn('lastSeen', reportedHost)
                self.assertIn('lastReported', reportedHost)
                self.assertIn('lastReportedLocal', reportedHost)
                
class GDB452(GenieTest):
    """Test IP address is seen when first status report is during a partition."""
    def setUp(self):
        if len(self.hosts.hosts) < 2:
            self.skipTest("Insufficient Hosts")
        super(GDB452, self).setUp()
        self.master = self.hosts.hosts[0]

    @expectedFailure
    def runTest(self):
        self.partition(self.master)
        sleep(3)
        for controlHost in self.hosts:
            done_nids=[]
            result, status = self.runScript("monitor", controlHost, False)
            self.assertEqual(0, status)
            data = loads(result)
            self.assertEqual(len(self.hosts), len(data))
            for reportedHost in data:
                host = None
                for localHost in self.hosts:
                    if localHost.properties['number'] == str(reportedHost['nid']):
                        host = localHost
                        break
                self.assertIsNotNone(host, "Monitor reported a host we could not find")
                self.assertNotIn(reportedHost['nid'], done_nids, "Monitor reported host %s twice" % reportedHost['nid'])
                done_nids.append(reportedHost['nid'])
                self.assertEqual(reportedHost['ip'], host.properties['application_address'])
