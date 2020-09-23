
__doc__ = '''
Lustre Utilities - Scripts for Lustre development

This is just the main routine.
lu_parser contains the code to make the parser,
and each file that lu_parser uses deals with a
subcommand.
'''

import lu_parser

if __name__ == '__main__':
    # make the parser, this will
    # build up a parser from a set of
    # commands based on lu_parser.subcommands
    parser = lu_parser.make_parser()

    # run the parser
    # figure out what subcommand to use
    # then delegate to the module
    # that implements that subcommand
    args = vars(parser.parse_args())
    
    # execute the subcommand which
    # is required to be called func
    if 'func' in args:
        args['func'](args)
        

