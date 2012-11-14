A guide to tinc-tailor internals
================================

Overview
--------

The basic mode of operation of tinc-tailor is to set up SSH connections to all
the hosts, and the run a sequence of commands on them.  These are fairly
flexible, the command can vary from host to host, including unique numbers,
host names, distro-specific commands etc.

A system of host properties exist, which allows any of these parameters to be
interpolated into transfered files or executed commands.


Important Classes
-----------------

### `Host`

`Host`s represent each host `tinc-tailor` knows about. The class contains an
ssh connection to the host and a dictionary of properties.

### `Action`

`Action`s represent the individual commands to be run a host. They can have
arbiary code in them, for example some send/recieve files, some manage file
system.

Each `Action` is constructed once, and the `run` method will get called for
each relevant host. The run method can then use any of the `Host` methods (for
example `async_command` to run a command, or `interpolate` to format data
specific to that machine).

The `Try` action is particularly useful.  It 'wraps' another action, turning
failures of that action into warnings.


### `Hostlist`

This class holds a group of `Host`s. It will initialize hosts, run an action on
all hosts, and has tools to get a subset of them.

### `Tailor`

This is the base class for all the "things" `tinc-tailor` can do.  There is one
for `tinc`, one for `cloudfabric`, one for running tests etc.
`setup_argparse()` and `argparse()` respectively define and handle the options
it takes.  The base class and `tinc-tailor` take care of setting up a `hosts`
member that contains the `Hostlist` object for the class.

Typically a `Tailor` will run a sequence of `Actions` on (a subset) of the
hosts in the list.

Tests
-----

There are currently no tests for `tinc-tailor` itself, however it contains an
infrastructure for running multinode tests.  These basically have the same
abilities as a 'Tailor' object, but the interface is a pyunit derived class
which is much more natural for test-writing.
