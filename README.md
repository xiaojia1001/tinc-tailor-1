
`tinc-tailor`
=============

`tinc-tailor` is a tool for managing a cluster of
[`CloudFabric`](http://www.geniedb.com/) servers using
[`tinc`](http://www.tinc-vpn.org/) as a VPN.


Requirements
------------
* [Python](http://www.python.org/)
* [Paramiko](http://www.lag.net/paramiko/)

installing
----------

`tinc-tailor` can be run from the source checked out from
<https://github.com/geniedb/tinc-tailor/>.  Run `sudo python setup.py install`
to install to the system or `python setup.py install --user` to install into
the user's home directory.

If you use pip just run
`pip install -r https://github.com/geniedb/tinc-tailor/raw/master/requirements.txt git+https://github.com/geniedb/tinc-tailor.git`
or
`pip install --install-option=--user -r https://github.com/geniedb/tinc-tailor/raw/master/requirements.txt git+https://github.com/geniedb/tinc-tailor.git`.

`hosts.list`
------------

This is a INI file where each section is a hostname that `tinc-tailor` will
considers to be in the cluster.  You should ensure the hostnames have no
hyphens in them as `tinc` does not like this. You should also ensure all the
hosts and your workstation can reach each other by these hostnames.

You may also add a `[DEFAULT]` section which sets defaults for all hosts.

You may use IP addresses instead of hostnames.


command reference
-----------------

*  `tinc-tailor tinc install [HOST]...`

   This performs the initial setup of these hosts, adding them to the cluster.
   Note that they must already be added to the `hosts.list` file. 

*  `tinc-tailor tinc remove [HOST]...`

   This removes the given hosts from the cluster, and removes tinc from them.
   The hosts should be removed from `hosts.list` after this is run.

*  `tinc-tailor tinc refresh`

   This reconfigures all hosts in `hosts.list` and ensures tincd is running on
   them.

*  `tinc-tailor cloudfabric [--channel {stable|unstable}] install [HOST]...`

   This installs cloudfabric on the given hosts.  The `--channel` option, which
   defaults to `unstable` controls which distribution channel of cloudfabric is
   installed.

*  `tinc-tailor cloudfabric remove [HOST]...`

   This removes cloudfabric from the given hosts.

*  `tinc-tailor cloudfabric refresh`

   This restarts cloudfabric on the given hosts.

*  `tinc-tailor check`

   This makes every host in `hosts.list` ping every other host by their private
   address

*  `tinc-tailor run COMMAND`

    This runs *command* on every host in `hosts.list`.
   

options
-------

`tinc-tailor` has some options to customize it's behavior:

*  `--help`
   Show a brief summary of the options and comamnds that `tinc-tailor` accepts.

   `--hosts-file FILENAME`
   
   This file tells `tinc-tailor` to read the given file instead of `hosts.list`
   (described above).

*  `--log-level (DEBUG|INFO|WARNING|ERROR|FATAL)`

   This option determines the amount of information to be logged. The default
   is WARNING, which prints very little.

*  `--global-log-level (DEBUG|INFO|WARNING|ERROR|FATAL)`

   As `--log-level`, but also log higher detail from python libraries used, for
   example for debugging the SSH connection.

examples
--------

Installing two nodes:

    $ cat > hosts.list
    [DEFAULT]
    netname=cf
    [node1.publicnetwork.com]
    [node2.publicnetwork.com]
    $ ./tinc-tailor tinc install node1.publicnetwork.com node2.publicnetwork.com

Verifying they work:

    $ ./tinc-tailor check

Adding an extra node:

    $ cat >> host.list
    [ondemand.cloudprovider.com]
    $ ./tinc-tailor tinc install ondemand.cloudprovider.com

Removing the first node:

    $ ./tinc-tailor tinc remove node2.publicnetwork.com
    $ cat > host.list
    [node1.publicnetwork.com]
    [ondemand.cloudprovider.com]
    key=/home/user/key.pem

Running a command on all the nodes:

    $ ./tinc-tailor run uname -r
    tailor.host.node1.publicnetwork.com: 2.6.32-279.5.2.el6.x86_64
    tailor.host.ondemand.cloudprovider.com: 2.6.32-5-amd64
