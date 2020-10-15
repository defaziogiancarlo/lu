import argparse
import pathlib
import tempfile

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
    parser.add('-s', '--source',
               help='the source directory to use')
    parser.add('-d', '--destination', required=True,
               help='the destination directory to use')


def create_and_copy(source_dir, dest_dir):
    '''create some files in source_dir, add some xattrs,
    cp the files to dest_dir and see if the xattrs are retained.'''
    # create a file in source_dir
    file_name = str(uuid.uuid4())
    source_file = source_dir / file_name
    dest_file = dest_dir / filename
    

    
    
# the function that actually executes the command
# this function deals with the arguments after they are
# parsed and are made into a dictionary
def main(args):
    # TODO make paths absolute if using root and a user
    # make pathlib.Path for source
    source_dir = arg.get('source')
    if source_dir is not None:
        source_dir = pathlib.Path(source_dir)
    else:
        source_dir = pathlib.Path.cwd()

    dest_dir = pathlib.Path(args['destination'])

    # TODO maybe check if source and dest are directories
    # TODO create the directories if they don't exist

    
    create_and_copy(source_dir, dest_dir)

    
    
    


    
if __name__ == '__main__':
    parser = set_up_parser()
    args = vars(parser.parse_args())
    main(args)
