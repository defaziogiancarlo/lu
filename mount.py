import argparse
import subprocess

import path

def mount_lustre(force=False):
    '''check if lustre is mounted, if not,
    mount it.'''
    lsmod_output = subprocess.run(['lsmod'], 
                                  capture_output=True).stdout.decode()

    llmount_path = str(path.find_lustre_path('llmount'))
    if 'lustre' not in lsmod_output or force:
        # need to run llmount
        subprocess.run([llmount_path], check=True)


# the usage string for this command
# it will be used as the main usage string
# if this command is called directly,
# or as the subcommand help string if called indirecly by lu
# required for use by lu
parser_help = '''mount lustre using the llmount.sh script.'''

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
    parser.add_argument('-f', '--force', action='store_true',
                        help=('run the mount script even if '
                        '\'lustre\' already shows up in lsmod'))

# the function that actually executes the command
# this function deals with the arguments after they are
# parsed and are made into a dictionary
def main(args):
    mount_lustre(force=args['force'])

if __name__ == '__main__':
    parser = set_up_parser()
    args = vars(parser.parse_args())
    main(args)
