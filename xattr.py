import argparse
import os
import pathlib
import subprocess
import tempfile
import uuid

# the usage string for this command
# it will be used as the main usage string
# if this command is called directly,
# or as the subcommand help string if called indirecly by lu
# required for use by lu
parser_help = '''Check if extended attributes (xattrs) are set and copied.'''

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
    parser.add_argument('-s', '--source',
                        help='the source directory to use')
    parser.add_argument('-d', '--destination', required=True,
                        help='the destination directory to use')
    parser.add_argument('-b', '--bidirectional', action='store_true')


def create_and_copy(source_dir, dest_dir):
    '''create some files in source_dir, add some xattrs,
    cp the files to dest_dir and see if the xattrs are retained.'''
    xattr_name = 'user.job'
    xattr_val = b'1234'

    
    # create a file in source_dir
    filename = str(uuid.uuid4())
    source_path = source_dir / filename
    dest_path = dest_dir / filename

    # make sure the directories exist
    source_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.parent.mkdir(parents=True, exist_ok=True)    
    
    # create and write to the source file
    with open(source_path, 'w') as f:
        text = '\n'.join(['Line ' + str(i) for i in range(1000)])
        f.write(text)
        
    # add an xattr to the source file
    os.setxattr(source_path, xattr_name, xattr_val)

    # copy to destination 
    subprocess.run(['cp', '--preserve=all', source_path, dest_path])

    # read the xattr
    copied_xattr = os.getxattr(dest_path, xattr_name)
    print('hello')
    print(str(copied_xattr))
    
    
# the function that actually executes the command
# this function deals with the arguments after they are
# parsed and are made into a dictionary
def main(args):
    # make pathlib.Path for source
    source_dir = args.get('source')
    if source_dir is not None:
        source_dir = pathlib.Path(source_dir).resolve()
    else:
        source_dir = pathlib.Path.cwd().resolve()

    dest_dir = pathlib.Path(args['destination']).resolve()
    
    create_and_copy(source_dir, dest_dir)

    if args.get('bidirectional'):
        create_and_copy(dest_dir, source_dir)
    
if __name__ == '__main__':
    parser = set_up_parser()
    args = vars(parser.parse_args())
    main(args)