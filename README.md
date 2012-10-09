
`tinc-tailor`
=============

`tinc-tailor` is a tool for managing a cluster of
[`CloudFabric`](http://www.geniedb.com/) servers using
[`tinc`](http://www.tinc-vpn.org/) as a VPN.


Requirements
------------
* [Python 2.7](http://www.python.org/)
* [Paramiko](http://www.lag.net/paramiko/)

installing
----------

`tinc-tailor` can be run from the source checked out from
<https://github.com/geniedb/tinc-tailor/>.  Run `sudo pythonsetup.py install`
to install to the system or `python setup.py install --user` to install into
the user's home directory.

`hosts.list`
------------

This is a list of hostnames, one per line, that `tinc-tailor` considers to be
in the cluster.  You should ensure the hostnames have no hyphens in them as
`tinc` does not like this. You should also ensure all the hosts and your
workstation can reach each other by these hostnames.

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

*  `tinc-tailor cloudfabric install [HOST]...`

   This installs cloudfabric on the given hosts.

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

*  `--host HOST`
   `--hosts-file FILENAME`
   These options control `tinc-tailor`'s awerness of hosts in the cluster. It
   combines the hosts given with the `--host` option with those read from the
   file specified with the `--hosts-file` option. The `--host` option may be
   given multiple times.

   Only if neither of these are set does `tinc-tailor` read from the default
   file `hosts.list`.

*  `--key KEYFILE`
   This option, which can be specified multiple times, specifies an ssh private
   key file to try to use to connect to the nodes.  In all cases
   `~/.ssh/id_rsa` and `~/.ssh/id_dsa` are tried to.  Note that `~/.ssh/config`
   is ignored.

*  `--netname NETNAME`
   For `tinc`, this specifies the name of the vpn network to create, and the
   name of the interface to create. For `cloudfabric` this specifies the
   interface for inter-node communication.

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
    node1.publicnetwork.com
    node2.publicnetwork.com
    $ ./tinc-tailor tinc install node1.publicnetwork.com node2.publicnetwork.com

Verifying they work:

    $ ./tinc-tailor check

Adding an extra node:

    $ cat >> host.list
    ondemand.cloudprovider.com
    $ ./tinc-tailor tinc install ondemand.cloudprovider.com

Removing the first node:

    $ ./tinc-tailor tinc remove node2.publicnetwork.com
    $ cat > host.list
    node1.publicnetwork.com
    ondemand.cloudprovider.com

Running a command on all the nodes:

    $ ./tinc-tailor run uname -r
    tailor.host.node1.publicnetwork.com: 2.6.32-279.5.2.el6.x86_64
    tailor.host.ondemand.cloudprovider.com: 2.6.32-5-amd64
