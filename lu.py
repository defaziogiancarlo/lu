__doc__ = '''
Lustre Utilities - Scripts for Lustre development

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

# include lu directory in path
import os
import sys

# get the path to where are the files are
# this should be set the top of the file
# for an executable version, and not matter otherwise
if 'lu_dir_path' in globals():
    sys.path.append(lu_dir_path)
 
import argparse

import cfg

# modules that implement subcommands
import bashize
import checkxattr
import mount
import path
import subcommand
import unmount
import xattr

# store each subcommand with its corresponding module
# they don't have to have the same name
subcommands = {'path' : path,
               'bashize' : bashize,
               'mount' : mount,
               'subcommand' : subcommand,
               'checkxattr' : checkxattr,
               'unmount' : unmount,
               'xattr' : xattr,
}

def add_module_parser(module_name, subcommand_name, subparsers):
    '''Add the parsing informations of a module associated with 
    as subcommand to the main parser.'''
    # create a subparser attached to subparsers
    module_parser = subparsers.add_parser(subcommand_name,
                                          description=module_name.parser_help)
    module_name.set_up_parser(module_parser)

# the main arugument parser
def make_parser():
    '''create the parser for the main command.
    add all the parsers for each subcommand.'''
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help', dest='subcommand')

    for subcommand, module in subcommands.items():
        add_module_parser(module, subcommand, subparsers)

    return parser

if __name__ == '__main__':
    # make the parser, this will
    # build up a parser from a set of
    # commands based on lu_parser.subcommands
    parser = make_parser()

    # run the parser
    # figure out what subcommand to use
    # then delegate to the module
    # that implements that subcommand
    args = vars(parser.parse_args())
    
    # execute the subcommand which
    # is required to be called func
    if 'func' in args:
        args['func'](args)
        

