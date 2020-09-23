import argparse
import pathlib
import sys

command_template='''
import argparse

# the usage string for this command
# it will be used as the main usage string
# if this command is called directly,
# or as the subcommand help string if called indirecly by lu
# required for use by lu
parser_help = ('') 

# a wrapper for set_up_parser_local
# allows for the case that an existing parser is
# being modified (which is the case when lu is using this
# module for a subcommand) and the case where this module
# us run as main, and no parser yet exists
def set_up_parser(parser=None):
    if parser is None:
        argparse.ArgumentParser(usage=parser_help)

    # lu expects the parser to a field called 'func'
    # which is set to 'main' by default
    parser.set_defaults(func=main)
    set_up_parser_local(parser)
    

# set up the parser for this command
# the parser passed in is either one passed from
# lu, or one just created for this module
# part of all this infrastructure is to hopefully make
# it not matter what the context is, so this fucntion
# can be written as if it's just for this module being
# called directly but it will work for lu as well
def set_up_parser_local(parser):
    pass

# the function that actually executes the command
# this function deals with the arguments after they are
# parsed and are made into a dictionary
def main(args):
    pass

if __name__ == '__main__':
    parser = set_up_parser_local()
    args = vars(paerser.parse_args())
    main(args)
'''

# the usage string for this command
# it will be used as the main usage string
# if this command is called directly,
# or as the subcommand help string if called indirecly by lu
# required for use by lu
parser_help = 'create a template for a lu subcommand'

# a wrapper for set_up_parser_local
# allows for the case that an existing parser is
# being modified (which is the case when lu is using this
# module for a subcommand) and the case where this module
# us run as main, and no parser yet exists
def set_up_parser(parser=None):
    if parser is None:
        argparse.ArgumentParser(usage=parser_help)

    # lu expects the parser to a field called 'func'
    # which is set to 'main' by default
    parser.set_defaults(func=main)
    set_up_parser_local(parser)

def set_up_parser_local(parser):
    parser.add_argument('path',
                        help='the path of the subcommand module')


# the function that actually executes the command
# this function deals with the arguments after they are
# parsed and are made into a dictionary
def main(args):
    path = pathlib.Path(args['path'])

    # add .py to path in needed
    if path.suffix != '.py':
        path = path.with_suffix('.py')

    # if path already exists don't overwrite it
    if path.exists():
        print(f'{str(path)} already exits, cannnot make template',
              file=sys.stderr)
        return

    with open(path, 'w') as f:
        f.write(command_template)


if __name__ == '__main__':
    parser = set_up_parser_local()
    args = vars(paerser.parse_args())
    main(args)
