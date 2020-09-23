__doc__ = '''
Find lustre on the system.
'''

import collections
import pathlib
import set_colors
import argparse


parser_help =('get a path within the lustre source code. '
        'This command will attempt to find the root of the lustre source code '
        'using user given base names or default base name. '
        'The check to make sure that the given base name is actually lustre is very weak '
        'it just checks if the path is a non-empty directory. '
        'Then a relative path will be added to give the full name.')

def set_up_parser(parser=None):
    # parser for this script alone
    
    if parser is None:
        parser = argparse.ArgumentParser(usage=parser_help)
    parser.add_argument('-s', '--show', action='store_true',
        help='show default base paths and relative paths.')
    parser.add_argument('-b', '--base_paths', nargs='*',
        help='set base paths, these paths will be used as the root of the lustre source code '
        'if they are non-empty directories. If none of the given base paths '
        'is plausibly the root of the lustre source code, the default base '
        'paths will be checked next, unless --default is set to no.')
    parser.add_argument('-d', '--default', choices=['yes', 'no', 'first'],
        help='control the order in which base paths are checked. '
        'if \'yes\' the default base paths will be checked after any given base paths. '
        'if \'no\' the default base paths will not be checked. '
        'if \'first\', the default base paths will be checked before any given base paths '
        'the default is \'yes\'')
    parser_mutex = parser.add_mutually_exclusive_group()
    parser_mutex.add_argument('-n', '--name',
        help='the name of some path in the lustre source tree. '
        'It will br translated into a path relative to the base path '
        'if it is a known name. To see the known names use --show.')
    parser_mutex.add_argument('-r', '--relative', nargs='?', const='',
        help='the relative path name. This will be added onto '
        'the lustre root path making <lustre source root>/<relative path>')
    parser.set_defaults(func=main)
    return parser


# places lustre is likely to be
default_lustre_paths = list(collections.OrderedDict.fromkeys([
    pathlib.Path.home() / 'lustre-release',
    pathlib.Path.home() / 'lustre',
    pathlib.Path('/g/g0/defazio1') / 'lustre-release',
    pathlib.Path('/g/g0/defazio1') / 'lustre',
]))

# important relative paths within lustre
relative_paths = {
    'lustre' : '',
    'lctl' : 'lustre/utils/lctl',
    'lfs' : 'lustre/utils/lfs',
    'llmount' : 'test/llmount.sh',
    'llmountcleanup' : 'test/llmountcleanup.sh',
    'checkpatch' : 'contrib/scripts/checkpatch.pl',
}


def show_paths():
    '''Show all default base paths,  as well as relative path names
    and their corresponding paths.'''
    set_colors.print_rgb((125,56,179), 'default base paths:')
    for p in default_lustre_paths:
        print(str(p))
    set_colors.print_rgb((125,56,179), 'relative paths:')
    for n,p in relative_paths.items():
        print(n + ' -> \'' + p + '\'')

def find_lustre(paths=None, check_defaults=None, check_defaults_first=None):
    '''Check file paths for likely root of lustre source
    the first that exists is considered to be lustre.
    Looks in possible_lustre_paths by default. Will also look in paths
    if given.
    '''
    # set optional values
    if check_defaults is None:
        check_defaults = True
    if check_defaults_first is None:
        check_defaults_first = False

    # select which paths to check and in which order
    all_paths = []
    if paths:
        all_paths += paths
    if check_defaults:
        if check_defaults_first:
            all_paths = default_lustre_paths + all_paths
        else:
            all_paths = all_paths + default_lustre_paths

    # find the first path that is a non-empty directory
    for path in all_paths:
        if path.is_dir() and list(path.glob('*')):
            return path
    raise FileNotFoundError('Unable to find lustre location in file system')

def lustre_paths(lustre_path):
    '''Create all the lustre paths.'''
    return {name : lustre_path / relative_path
                    for name, relative_path
                    in relative_paths.items()}

def find_path(lustre_path, rel_path_name):
    '''Try to find a single lustre path'''
    rel_path = relative_paths.get(rel_path_name)
    if rel_path is None:
        return None
    return lustre_path / rel_path

def main(args):
    '''Deal with arguments and call appropriate
    functions.
    '''
    if not isinstance(args, dict):
        args = vars(args)
    
    if args['show']:
        show_paths()

    base_paths = args.get('base_paths')
    if base_paths == []:
        base_paths = None

    default = args.get('default')
    relative = args.get('relative')
    check_defaults = None
    check_defaults_first = None
    if default == 'yes':
        check_defaults = True
        check_defaults_first = False
    if default == 'first':
        check_defaults = True
        check_defaults_first = True
    if default == 'no':
        check_defaults = False
        check_defaults_first = False
    lustre_root = find_lustre(base_paths, 
                              check_defaults,
                              check_defaults_first)

    # mutally exclusive if blocks based on parser
    if args['name'] is not None:
        full_path = find_path(lustre_root, args['name'])
        if full_path is not None:
            print(full_path)
    if args['relative']:
        print(lustre_root / relative)
    
        
if __name__ == '__main__':
    parser = set_up_parser()
    args = vars(parser.parse_args())
    main(args)







