import argparse
import copy
import os
import pathlib
import sys

import yaml

# cfg will attempt to retrive a configuration
# file the first time it is imported
import cfg

# the usage string for this command
# it will be used as the main usage string
# if this command is called directly,
# or as the subcommand help string if called indirecly by lu
# required for use by lu
parser_help = '''Install lu on your system. This will create
a configuration file at \'~/.lu.yaml\' and put an executable
version of lu in \'~/bin\'.'''

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
    parser.add_argument('-p, ''--python', 
                       help=('pick a path to use for python. '
                       'otherwise \'which python3\' is used.'))
    parser.add_argument('-b', '--bin',
                        help='pick a path to put the executable version of lu at, '
                        'the default is ~/bin')


def make_executable_lu(lu_path, lu_dir_path, python_path, executable_path):
    '''Prepend !#<python>
    and define lu_dir_path which is used to find
    all the files that need to be imported.'''
    text = None
    with open(lu_path, 'r') as lu_file:
        text = lu_file.read()

    # TODO make executable path dir if it doesn't exist
    executable_path.parent.mkdir(parents=True, exist_ok=True)
    with open(executable_path, 'w') as executable_file:
        executable_file.write('#!' + python_path + '\n\n')
        executable_file.write(f'lu_dir_path = \'{lu_dir_path}\'\n\n')
        executable_file.write(text)
    executable_path.chmod(0o744)
    
def make_config_file(lu_dir_path, python_path):
    '''make config file and put in home directory.
    sets default values:
        username from environment
        user_home from environment
        lu_path from this file's parent
        user_bin assumed to be ~/bin
        python is the version of python currently running'''
    if os.environ['USER'] == 'root':
        # don't make configuration file
        # it will belong to root, also this program shouldn't
        # mess with the home directory of the root user
        print('Warning: no lu configuration file made. '
              'lu configuration file should not be made as root.',
              file=sys.stderr)
        return
    else:
        # put defaults into cfg.env
            
        env = copy.deepcopy(cfg.env)
        env['username'] = os.environ['USER']
        env['user_home'] = os.environ['HOME']
        env['lu_dir_path'] = str(lu_dir_path)
        env['user_bin'] = str(pathlib.Path(os.environ['HOME']) / 'bin')
        env['python'] = str(python_path)

        config_path = pathlib.Path(os.environ['HOME']) / '.lu.yaml'
        with open(config_path, 'w') as f:
            dump_text = yaml.dump(env)
            f.write(dump_text)
            
# the function that actually executes the command
# this function deals with the arguments after they are
# parsed and are made into a dictionary
def main(args):
    # get the directory of this file
    # which should be the lu directory
    lu_dir_path = pathlib.Path(__file__).parent.absolute()
    lu_path = lu_dir_path / 'lu.py'
    python_path = args.get('python')
    if python_path is None:
        # get this python
        python_path = sys.executable

    executable_path = pathlib.Path(os.environ['HOME']) / 'bin' / 'lu'

    make_executable_lu(lu_path, lu_dir_path, python_path, executable_path)

    make_config_file(lu_dir_path, python_path)
    # set lu.py to include the lu path
    # set lu.py to be run with python_path
    # make lu executable and put it in ~/bin, make ~/bin if it doesn't exist
    # if making ~/bin, warn user and say that it should be put into PATH
    # create .lu.yaml and initialize it with default values



if __name__ == '__main__':
    parser = set_up_parser()
    args = vars(parser.parse_args())
    main(args)
