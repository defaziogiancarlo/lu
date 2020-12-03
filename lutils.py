__doc__ = '''
Basic utilities
'''

import re
import os
import pathlib
import shutil
import subprocess

import cfg

# some useful regexes
# a single ip4 octet 1,2,or 3 digits  0-255
ip4_octet_pattern_str = r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
# a single ip4 octet followed by a '.'
ip4_octet_dot_pattern_str = r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)'
# a full ip4 address  <octet>.<octet>.<octet>.<octet>
ip4_re_str = ip4_octet_dot_pattern_str + r'{3}' + ip4_octet_pattern_str


# printing in color
foreground = '\033[38;2;{r};{g};{b}m'
background = '\033[48;2;{r};{g};{b}m'

def set_foreground_rgb(r,g,b):
    print(foreground.format(r=r,g=g,b=b), end='')

def set_background_rgb(r,g,b):
    print(background.format(r=r,g=g,b=b), end='')

def reset_colors():
    print('\033[0m', end='')

def print_rgb(rgb, *args, **kwargs):
    set_foreground_rgb(*rgb)
    print(*args, **kwargs)
    reset_colors()


# who am I?
def check_machine(name):
    '''Check if the current is name.'''
    machine = os.environ['HOSTNAME']
    if machine != name:
        raise AssertionError(
            'Using the wrong machine, ' 
            'currently using {}, '
            'should be using {}.'.format(machine, name))


# setting up lustre
# TODO, this is limited to 192.168 ... addresses, which may not work for different setups
# should grab the correct ip regardless
def set_ip(hostname=None):
    '''Set the ip address in /etc/hosts to 
    match that of ifconfig. This is for lustre/tests/llmount.sh'''

    if hostname is None:
        hostname = os.environ['HOSTNAME']

    print(hostname)

    ip_data = subprocess.run(['ifconfig'], 
                             capture_output=True).stdout.decode()

    # the only match is the ip address
    ip4_pattern = re.compile(ip4_re_str)
    ifconfig_ip = ip4_pattern.search(ip_data).group(0)
    if ifconfig_ip is None:
        raise Exception('no usable ip in ifconfig')

    # now get the ip address in /etc/hosts for hostname
    # also save the contents of /etc/hosts because it might
    # be needed later
    etc_ip = None
    hosts = None
    with open('/etc/hosts', 'r') as f:
        hosts = f.read()

    for line in hosts.split('\n'):
        if hostname in line:
            # avoid commented lines
            if line.strip()[0] != '#':
                etc_ip = ip4_pattern.match(line).group(0)

    if etc_ip is None:
        raise Exception('no usable ip in /etc/hosts')

    # if the are equal, nothing to do
    if ifconfig_ip == etc_ip:
        return

    # replace etc_ip in /etc/hosts with ifconfig_ip
    # NOTE this assumes that this ip appears only once
    # or this might break things
    hosts = hosts.replace(etc_ip, ifconfig_ip)

    # overwrite /etc/hosts
    with open('/etc/hosts', 'w') as f:
        f.write(hosts)


def mount_lustre(force=False):
    '''check if lustre is mounted, if not,
    mount it.'''

    # the ip frequently changes for vms
    set_ip()

    lsmod_output = subprocess.run(['lsmod'], 
                                  capture_output=True).stdout.decode()

    llmount_path = str(find_lustre_path('llmount'))
    if 'lustre' not in lsmod_output or force:
        # need to run llmount
        subprocess.run([llmount_path], check=True)

def unmount_lustre():
    '''check if lustre is mounted, if so, unmount it'''
    lsmod_output = subprocess.run(['lsmod'], 
                                  capture_output=True).stdout.decode()

    llmountcleanup_path = str(find_lustre_path('llmountcleanup'))
    if 'lustre' in lsmod_output:
        subprocess.run([llmountcleanup_path], check=True)
        
    
def build_lustre(user_name=None, full=True):
    '''Build lustre, if full is set to false, only do that make step'''

    if user_name is None:
        user_name = cfg.env.get('username')
    if user_name is None:
        sys.exit('ERROR: no username given or found in configuration file.')

    # build as non-root user
    lustre_path = find_lustre()
    if full:
        subprocess.run(['sudo', '-u', user_name, 'make', 'clean'], cwd=lustre_path)
        subprocess.run(['sudo', '-u', user_name, 'sh', 'autogen.sh'], cwd=lustre_path)
        subprocess.run(['sudo', '-u', user_name, './configure'], cwd=lustre_path)
    subprocess.run(['sudo', '-u', user_name, 'make', '-j12'], cwd=lustre_path)



## lust paths
def make_default_lustre_paths():
    '''use the configuration path if it exits,
    otherwise check the home directory'''
    paths = []

    # the easy case, it's set in the configuration file
    if cfg.env.get('lustre_path'):
        paths.append(pathlib.Path(cfg.env['lustre_path']))
    else:
        paths.append(pathlib.Path.home() / 'lustre-release')
        paths.append(pathlib.Path.home() / 'lustre')
    return paths

# determine paths at module load time
default_lustre_paths = make_default_lustre_paths()

# important relative paths within lustre
lustre_relative_paths = {
    'lustre' : '',
    'lctl' : 'lustre/utils/lctl',
    'lfs' : 'lustre/utils/lfs',
    'llmount' : 'lustre/tests/llmount.sh',
    'llmountcleanup' : 'lustre/tests/llmountcleanup.sh',
    'checkpatch' : 'contrib/scripts/checkpatch.pl',
    'auster' : 'lustre/tests/auster'
}

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

def lustre_paths(relative_path):
    '''Create all the lustre paths.'''
    return {name : lustre_path / relative_path
                    for name, relative_path
                    in lustre_relative_paths.items()}

def find_path(lustre_path, rel_path_name):
    '''Try to find a single lustre path'''
    rel_path =lustre_relative_paths.get(rel_path_name)
    if rel_path is None:
        return None
    return lustre_path / rel_path

def find_lustre_path(rel_path_name):
    '''guess the location of lustre
    and find the path.'''
    lustre_path = find_lustre()
    return find_path(lustre_path, rel_path_name)


def remove_dir_contents(dir_path):
    '''remove the contents of a directory
    but not the directory itself. Directory shouldn't contain
    symlinks.'''
    dir_path = pathlib.Path(dir_path)
    for path in dir_path.glob('*'):
        if path.is_dir:
            shutil.rmtree(path)
        else:
            path.unlink()

