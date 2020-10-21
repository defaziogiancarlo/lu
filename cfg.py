__doc__ = '''a place to hold configuration variables'''

import json
import pathlib
import os

# AUTOGENERATED
cfg_path = pathlib.Path('/home/defazio1/.lu.json')

# holds all possible configuration values
# meant to be set whenever a script is called
# and then can be used by scripts
env = {"username"    : None,
       "user_home"   : None,
       "lustre_path" : None,
       "lu_path"     : None,
       "user_bin"    : None,
       "python"      : None,
}

def set_env():
    '''attempt to set environment variables.
    will look for .lu.json'''
    cfg_file_vals = None
    with open(cfg_path, 'r') as f:
        cfg_file_vals = json.load(f)

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

    
