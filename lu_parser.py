__doc__ = '''
Master parser for all commands
'''

import argparse

import lustre_utils

import bashize
import lustre_paths

# store each subcommand with it's corresponding module
subcommands = {'path' : lustre_paths,
               'bashize' : bashize,
}

# the main arugument parser
def make_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help', dest='subcommand')

    for subcommand, module in subcommands:
        lustre_utils.add_module_parser(module, subcommand, subparsers)

    return parser


    
    # path subparser
    help_string = ('get a path within the lustre source code. '
                   'This command will attempt to find the root of the lustre source code '
                   'using user given base names or default base name. '
                   'The check to make sure that the given base name is actually lustre is very weak '
                   'it just checks if the path is a non-empty directory. '
                   'Then a relative path will be added to give the full name.')
    sp = subparsers.add_parser('path', help=help_string)
    sp.add_argument('-s', '--show', action='store_true',
        help='show default base paths and relative paths.')
    sp.add_argument('-b', '--base_paths', nargs='*',
        help='set base paths, these paths will be used as the root of the lustre source code '
        'if they are non-empty directories. If none of the given base paths '
        'is plausibly the root of the lustre source code, the default base '
        'paths will be checked next, unless --default is set to no.')
    sp.add_argument('-d', '--default', choices=['yes', 'no', 'first'],
        help='control the order in which base paths are checked. '
        'if \'yes\' the default base paths will be checked after any given base paths. '
        'if \'no\' the default base paths will not be checked. '
        'if \'first\', the default base paths will be checked before any given base paths '
        'the default is \'yes\'')
    sp_mutex = sp.add_mutually_exclusive_group()
    sp_mutex.add_argument('-n', '--name',
        help='the name of some path in the lustre source tree. '
        'It will br translated into a path relative to the base path '
        'if it is a known name. To see the known names use --show.')
    sp_mutex.add_argument('-r', '--relative', nargs='?', const='',
        help='the relative path name. This will be added onto '
        'the lustre root path making <lustre source root>/<relative path>')
    sp.set_defaults(func=lustre_paths.main)


    # bahsize
    help_string = ('Create a bash script at the given path.'
                   'If no file exists, create one.'
                   'If a file does exist but does not start with'
                   '#!, add #!/bin/bash and make executable,'
                   'if #! already exists, do nothing.')
    bsp = subparsers.add_parser('path', help=help_string)
    subpar

    
    return parser
