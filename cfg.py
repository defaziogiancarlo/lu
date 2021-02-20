__doc__ = '''a place to hold configuration variables'''

import os
import pathlib
import pwd
import sys

import yaml

cfg_file_name = '.lu.yaml'

# holds all possible configuration values
# meant to be set whenever a script is called
# and then can be used by scripts
env = {'username'    : None,
       'user_home'   : None,
       'lustre_path' : None,
       'lu_dir_path'     : None,
       'user_bin'    : None,
       'python'      : None,
}

def set_env():
    '''attempt to set environment variables.
    will look for .lu.yaml'''
    # find the cfg_path
    cfg_path = None
    # check if root, if root, check for SUDO_USER
    # the configuration file of SUDO_USER WILL be used
    # if there is no SUDO_USER in the environment, then
    # you're running this program in a way that makes no sense
    # because you shouldn't be logged in as root,
    # or have doen some weird sudo/su stuff 
    if os.environ['USER'] == 'root':
        # currently root, but due to using sudo
        if 'SUDO_USER' in os.environ:
            passwd_info = pwd.getpwnam(os.environ['SUDO_USER'])
            cfg_path = passwd_info.pw_dir
        else:
            # no configuration set
            # this program isn't set up for a user logged in as root
            sys.exit('Warning: no lu configuration set. '
                  'lu is not meant for users logged in as root. '
                  'If you\'re not logged in as root, this is a bug.')
    else:
        cfg_path = os.environ['HOME']
    cfg_path = pathlib.Path(cfg_path) / cfg_file_name
    
    # if not file, don't set anything
    if not cfg_path.is_file():
        print('Warning: No lu configuration file found. '
              'This is normal when setting up lu.',
              file=sys.stderr)
        return

    cfg_file_vals = None
    with open(cfg_path, 'r') as f:
        cfg_file_vals = yaml.load(f, Loader=yaml.Loader)

    # set the values in env
    for key in env.keys():
        if key in cfg_file_vals:
            env[key] = cfg_file_vals[key]

    for key in cfg_file_vals.keys():
        if key not in env:
            print('warning: invalid config value \'{}\' in {}'.format(
                str(key), str(cfg_path)))

            
# set env varables, this should only happen once
set_env()

    
