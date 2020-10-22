import argparse
import pathlib

# cfg will attempt to retrive a configuration
# file the first time it is imported
import cfg

# the usage string for this command
# it will be used as the main usage string
# if this command is called directly,
# or as the subcommand help string if called indirecly by lu
# required for use by lu
parser_help = '''Install lu on your system. This will create
a configuration file at \'~/.lu.json\' and put an executable
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
                        help='pick a path to put the executable version of lu at,
                        the default is ~/bin')


def make_executable_lu(lu_path, lu_dir_path, python_path, executable_path):
    '''Prepend !#<python>
    and define lu_dir_path which is used to find
    all the files that need to be imported.'''
    text = None
    with open(lu_path, 'r') as lu_file:
        text = lu_file.read()
    
    # TODO make executable path dir if it doesn't exist
    with open(executable, 'w') as executable_file:
        executable_file.write('#!' + python_path + '\n')
        executable_file.write(f'lu_dir_path = \'{lu_dir_path}\'\n')
        executable_file.write(text)
    



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
        python_path = subprocess.run(['which', 'python3'], 
                                     capture_output=True,
                                     check=True).stdout.decode()
    # set lu.py to include the lu path
    # set lu.py to be run with python_path
    # make lu executable and put it in ~/bin, make ~/bin if it doesn't exist
    # if making ~/bin, warn user and say that it should be put into PATH
    # create .lu.json and initialize it with default values



if __name__ == '__main__':
    parser = set_up_parser()
    args = vars(parser.parse_args())
    main(args)
