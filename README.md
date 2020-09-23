# lu
Lustre Utilities

This is a conglomeration of various commands I use
for lustre development, and some commands that are
or only tangentially related. The whole point is to not
have to remember which script I wrote for what task and
how to use that script. `lu` is just a single command with
lots of subcommands, as well as the usage information for
each subcommand.

`lu` is set up so that each subcommand can be run independently,
meaning that it's not neccesary to call
```
lu <subcommand> <flags/args>
```
to use a subcommand. Each subcommand is a python script that
can be run directly
```
python3 <subcommand>.py <flags/args>
```

However, the subcommands must adhere to an interface to work
with `lu`. The `lu subcommand` subcommand will generate a new
`.py` file that is a template for a compliant subcommand.



