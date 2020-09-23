__doc__ = '''
Master parser for all commands.

This argparser is designed to build up
one large argparser from a set of module,
each of which implements a subcommand and can
be called individually.

Each module the implements a subcommand should have:

A string called 'parser_help', which is just the main
help string for its parser, The one that can be optionally
specified when adding a subparser.

A function called 'set_up_parser'.
This function should optionally take an existing parser
as an input, and have a default value of None for the parser. 
In the case that an existing parser is passed in
(as one is in the function add_module_parser), the parser
is modified to have a new subcommand from the module.
If the parser is None, which should happen when the module
is run as __main__ and not part of lu, the function should 
make a new parser.
The module should set the appropriate function to 
acutally execute the command to 'func' in the parser.
Also, that function should be able to accept args resulting
from the argparse as a dict.

See any of modules in 'subcommands' for examples. 
'''

import argparse

# modules that implement subcommands
import bashize
import subcommand
import path

# store each subcommand with its corresponding module
subcommands = {'path' : path,
               'bashize' : bashize,
               'subcommand' : subcommand,
}

def add_module_parser(module_name, subcommand_name, subparsers):
    '''Add the parser of a module to the main parser.'''
    # create a subparser attached to subparsers
    module_parser = subparsers.add_parser(subcommand_name,
                                          help=module_name.parser_help)
    module_name.set_up_parser(module_parser)


# the main arugument parser
def make_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help', dest='subcommand')

    for subcommand, module in subcommands.items():
        add_module_parser(module, subcommand, subparsers)

    return parser

