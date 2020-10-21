import argparse
import os
import pathlib
import subprocess
import tempfile
import uuid

# NOTE the utilities setfattr, getfattr exist and can do all this
# too. However they were intalled by default on ubuntu when I wrote this.

# the usage string for this command
# it will be used as the main usage string
# if this command is called directly,
# or as the subcommand help string if called indirecly by lu
# required for use by lu
parser_help = '''Get, set, and list extended attribute (xattrs)'''

# a wrapper for set_up_parser_local
# allows for the case that an existing parser is
# being modified (which is the case when lu is using this
# module for a subcommand) and the case where this module
# is run as main, and no parser yet exists
def set_up_parser(parser=None):
    if parser is None:
        parser = argparse.ArgumentParser(usage=parser_help)

    # lu expects the parser to a field called 'func'
    # which is set to 'main' by default
    parser.set_defaults(func=main)
    set_up_parser_local(parser)
    return parser


# set up the parser for this command
# the parser passed in is either one passed from
# lu, or one just created for this module
# part of all this infrastructure is to hopefully make
# it not matter what the context is, so this function
# can be written as if it's just for this module being
# called directly but it will work for lu as well
def set_up_parser_local(parser):
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-g', '--get', nargs=2,
                       metavar=('filename','xattr_name'),
                       help='get the value of an xattr')
    group.add_argument('-s', '--set', nargs=3,
                       metavar=('filename', 'xattr_name', 'value'),
                       help='set the value of an xattr')
    group.add_argument('-l', '--list',
                       metavar='filename',
                       help='list the xattr names')

# the function that actually executes the command
# this function deals with the arguments after they are
# parsed and are made into a dictionary
def main(args):
    if args.get('get'):
        path, name = args['get']
        val = os.getxattr(path, name)
        print(str(val))

    elif args.get('set'):
        path, name, value = args['set']
        os.setxattr(path, name, bytes(value, 'utf-8'))

    elif args.get('list'):
        path = args['list']
        print(os.listxattr(path))

        
    
if __name__ == '__main__':
    parser = set_up_parser()
    args = vars(parser.parse_args())
    main(args)
