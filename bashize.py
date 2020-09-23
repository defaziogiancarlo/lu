import argparse
import pathlib
import shutil
import subprocess
import sys
import uuid

# the usage string for this command
# it will be used as the main usage string
# if this command is called directly,
# or as the subcommand help string if called indirecly by lu
# required for use by lu
parser_help = ('Create a bash script with at the path given by the user.'
               'Prepend the line #!/bin/bash and make executable.'
               'Find the correct location of bash if not /bin/bash.'
               'If the file already begins with \'#!\' or is not a normal'
               'file, make no changes to it.')

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
    parser.add_argument('path',
                        help='the path to the bash script')
    parser.set_defaults(func=main)

# the function that actually executes the command
# this function deals with the arguments after they are
# parsed and are made into a dictionary
# TODO could deal with race conditions if you
# TODO really like pain, make an atomic file modification
# TODO function
def main(args):
    '''Create a bash script at the given path.
    If no file exists, create one.
    If a file does exist but does not start with
    #!, add #!/bin/bash and make executable,
    if #! already exists, do nothing.
    '''
    path = pathlib.Path(args['path'])

    # get bash's path
    which_bash_path = subprocess.run(['which', 'bash'],
                                     capture_output=True,
                                     check=True)
    shebangbash = '#!' + which_bash_path.stdout.decode() + '\n'

    # ensure something exists at path
    path.touch()

    # is path is something besides a normal file, don't mess with it
    if not path.is_file():
        raise FileNotFoundError(str(path) + ' is not normal a'
                                    ' normal file, cannot bashize')

    # check if #! line already exists
    # in which case there's nothing to do
    with open(path, 'rb') as f:
        first_2 = f.read(2)
        if first_2 == b'#!':
            print(str(path) + ' already starts with \'!#',
                  file=sys.stderr)
            return

    # make new file
    current_text = path.read_text()
    f_name = pathlib.Path(str(uuid.uuid4()))
    with open(f_name, 'w') as f:
        f.write(shebangbash)
        f.write(current_text)

    # overwrite and set permisssions
    shutil.move(f_name, path)
    path.chmod(0o744)

if __name__ == '__main__':
    parser = set_up_parser()
    args = vars(parser.parse_args())
    main(args)
