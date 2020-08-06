__doc__ = '''
Lustre Utilities - Scripts for Lustre development
'''

import argparse

import set_colors
import bashize
import lustre_paths

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='sub-command help', dest='subcommand')
#parser_a = subparsers.add_parser('a', help='a help')
#parser_a.add_argument('bar', type=int, help='bar help')
#parser_b = subparsers.add_parser('b', help='b help')
#parser_b.add_argument('--baz', choices='XYZ', help='baz help')

#parser_bashize = subparsers.add_parser('bashize')
#parser_bashize.add_argument('filename')


parser_path = subparsers.add_parser('path', help=lustre_paths.parser_help)
lustre_paths.set_up_parser(parser_path)



# deal with lustre_path module
# parser_path = subparsers.add_parser('path',
#             help='get a path within the lustre source code. '
#             'This command will attempt to find the root of the lustre source code '
#             'using user given base names or default base name. '
#             'The check to make sure that the given base name is actually lustre is very weak '
#             'it just checks if the path is a non-empty directory. '
#             'Then a relative path will be added to give the full name.')
# parser_path.add_argument('-s', '--show', action='store_true',
#                          help='show default base paths and relative paths.')
# parser_path.add_argument('-b', '--base_paths', nargs='*',
#                          help='set base paths, these paths will be used as the root of the lustre source code '
#                          'if they are non-empty directories. If none of the given base paths '
#                          'is plausibly the root of the lustre source code, the default base '
#                          'paths will be checked next, unless --default is set to no.')
# parser_path.add_argument('-d', '--default', choices=['yes', 'no', 'first'],
#                          help='control the order in which base paths are checked. '
#                          'if \'yes\' the default base paths will be checked after any given base paths. '
#                          'if \'no\' the default base paths will not be checked. '
#                          'if \'first\', the default base paths will be checked before any given base paths '
#                          'the default is \'yes\'')
# parser_path_mutex = parser_path.add_mutually_exclusive_group()
# parser_path_mutex.add_argument('-n', '--name',
#                          help='the name of some path in the lustre source tree. '
#                          'It will br translated into a path relative to the base path '
#                          'if it is a known name. To see the known names use --show.')
# parser_path_mutex.add_argument('-r', '--relative', nargs='?', const='',
#                          help='the relative path name. This will be added onto '
#                          'the lustre root path making <lustre source root>/<relative path>')


if __name__ == '__main__':
    args = vars(parser.parse_args())
    print(args)
    subcommand = args.get('subcommand')

    if subcommand == 'path':
        lustre_paths.main(args)
