# lu
Lustre Utilities

This is a conglomeration of various commands I use
for lustre development, and some commands that are
or only tangentially related. The whole point is to not
have to remember which script I wrote for what task and
how to use that script. `lu` is just a single command with
lots of subcommands, as well as the usage information for
each subcommand.

## Installation
First download from git and run the setup script. This assumes you have
an up-to-date version of python. At least 3.7. The setup script should not
be run when logged in as root, or when using sudo.
```shell
gianni@computer:~$ git clone https://github.com/defaziogiancarlo/lu.git
...
gianni@computer:~$ cd lu
gianni@computer:~$ python3 setup.py
```
This will create `~/bin/lu` which is the executable version of `lu.py` with some
extra information for the python version and the location of where the lu repo is.
It will also create `~/.lu.yaml` which is the lu configuration file. This file will
be used even when lu is used with sudo.

## Configuration

The configuration file will be a `~/.lu.yaml` after running the setup script.
It will be filled with default values. The important one that needs to be set is
the location of the lustre repo. For all path values in the configurations file,
absolute paths should be used.

## Subcommands
`lu` is set up so that each subcommand can be run independently,
meaning that it's not neccesary to call
```shell
lu <subcommand> <flags/args>
```
to use a subcommand.
Each subcommand is a python script that
can be run directly. 
```shell
python3 <subcommand>.py <flags/args>
```
However, not all modules are subcommands.
For example the [cfg](cfg.py) and [lutils](lutils.py) are not meant to
be run as commands and aren't listed as subcommands by `lu`.

The subcommands must adhere to an interface to work
with `lu`. The `lu subcommand` subcommand will generate a new
`.py` file that is a template for a compliant subcommand. The template
sets up a system that allows each command to create and use its own argument
parser when called individually, or incorporate its argument parser
into that of `lu` when used as a subcommand of `lu`.

## sudo usage
`lu` is meant for a specific use case. Which is for a user who is not
logged in as `root` but does have `sudo` privleges. However, this user
can't make any changes to directories owned by root.

Consequently, `lu` uses a bizzare and probably idiotic way of dealing with this.
The [setup](setup.py) command creates a configuration file and an executable version
of `lu`. Then, this executable version can be called by the user when using sudo or not.
However, unless you preseve path variables, the absolute path needs to be used using sudo.
