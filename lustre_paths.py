__doc__ = '''
Find lustre on the system.
'''

from pathlib import Path

# places luste is likely to be
default_lustre_paths = [
    Path.home() / 'lustre-release',
    Path.home() / 'lustre',
]

# important relative paths within lustre
relative_paths = {
    'lctl' : 'lustre/utils/lctl',
    'lfs' : 'lustre/utils/lfs',
    'llmount' : 'test/llmount.sh',
    'llmountcleanup' : 'test/llmountcleanup.sh',
}

def find_lustre(paths=None, check_defaults=True, check_defaults_first=False):
    '''Check file paths for likely root of lustre source
    the first that exists is considered to be lustre.
    Looks in possible_lustre_paths by default. Will also look in paths
    if given.
    '''
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









