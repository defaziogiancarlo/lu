import argparse
import pathlib
import re
import subprocess

import cfg

import path
import utils

# TODO, this is limited to 192.168 ... addresses, which may not work for different setups
# should grab the correct ip regardless
# TODO hostname can be gotten from the environment
def set_ip(hostname='vmlustre'):
    '''Set the ip address in /etc/hosts to 
    match that of ifconfig. This is for lustre/tests/llmount.sh'''

    ip_data = subprocess.run(['ifconfig'], 
                             capture_output=True).stdout.decode()

	# the only match is the ip address
    ip4_pattern = re.compile(utils.ip4_re_str)
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
        

# TODO maybe get user_name from environment
def setup_quota(fs_path='/mnt/lustre', user_name=None):
    '''set up lustre for quotas.'''

    if user_name is None:
        user_name = cfg.env.get('username')
    if user_name is None:
        sys.exit('ERROR: no username given or found in configuration file.')
    
    # make the lustre file system writable
    mnt = pathlib.Path(fs_path)
    mnt.chmod(0o777)

    # find lctl
    lctl_path = str(path.find_lustre_path('lctl'))
    lfs_path = str(path.find_lustre_path('lfs'))

    # set up logging for quotas
    subprocess.run([lctl_path, 'set_param', 'debug=-1'])
    subprocess.run([lctl_path, 'set_param', 'subsystem_debug=lquota'])

    # turn on quotas for osts and mdts for users
    subprocess.run([lctl_path, 'conf_param', 'lustre.quota.ost=u'])
    subprocess.run([lctl_path, 'conf_param', 'lustre.quota.mdt=u'])

    # set grace periods for block and inode for users
    subprocess.run([lfs_path, 'setquota', '-t', '-u', '--block-grace', 
                    '20w4d12h3m13s', '--inode-grace', '7200', fs_path])    

    # set block limits for the user
    subprocess.run([lfs_path, 'setquota', '-u', user_name, 
                    '--block-softlimit', '20M', 
                    '--block-hardlimit', '30M', 
                    fs_path])
    subprocess.run([lfs_path, 'setquota', '-u', user_name, 
                    '--inode-softlimit', '2048', 
                    '--inode-hardlimit', '3072', 
                    fs_path])
    
def mount_lustre():
    '''check if lustre is mounted, if not,
    mount it.'''
    lsmod_output = subprocess.run(['lsmod'], 
                                  capture_output=True).stdout.decode()

    llmount_path = str(path.find_lustre_path('llmount'))
    if 'lustre' not in lsmod_output:
        # need to run llmount
        subprocess.run([llmount_path])

def unmount_lustre():
    '''check if lustre is mounted, if so, unmount it'''
    lsmod_output = subprocess.run(['lsmod'], 
                                  capture_output=True).stdout.decode()

    llmountcleanup_path = str(path.find_lustre_path('llmountcleanup'))
    if 'lustre' in lsmod_output:
        subprocess.run([llmountcleanup_path])
        
    
def build_lustre(user_name=None):

    if user_name is None:
        user_name = cfg.env.get('username')
    if user_name is None:
        sys.exit('ERROR: no username given or found in configuration file.')

    # build as non-root user
    lustre_path = path.find_lustre()
    subprocess.run(['sudo', '-u', user_name, 'make', 'clean'], cwd=lustre_path)
    subprocess.run(['sudo', '-u', user_name, 'sh', 'autogen.sh'], cwd=lustre_path)
    subprocess.run(['sudo', '-u', user_name, './configure'], cwd=lustre_path)
    subprocess.run(['sudo', '-u', user_name, 'make', '-j12'], cwd=lustre_path)


def setup_quota_test():
    '''assumes no lustre build or installed'''
    #build_lustre()
    #set_ip()
    #mount_lustre()
    setup_quota()

def resetup_quota_test(full=False, user_name=None):
    '''assumes lustre needs to be remade and reinstalled'''

    if user_name is None:
        user_name = cfg.env.get('username')
    if user_name is None:
        sys.exit('ERROR: no username given or found in configuration file.')

    unmount_lustre()
    if full:
        subprocess.run(['sudo', '-u', user_name, 'make', 'clean'], cwd=lustre_root)
        subprocess.run(['sudo', '-u', user_name,'sh', 'autogen.sh'], cwd=lustre_root)
        subprocess.run(['sudo', '-u', user_name,'./configure'], cwd=lustre_root)
    subprocess.run(['sudo', '-u', user_name,'make', '-j12'], cwd=lustre_root)
    mount_lustre()
    setup_quota()


# the usage string for this command
# it will be used as the main usage string
# if this command is called directly,
# or as the subcommand help string if called indirecly by lu
# required for use by lu
parser_help = '''Some arguments need sudo, this is specified
per argument.
'''

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
    parser.add_argument('-s', '--set-ip', action='store_true',
                        help=('Requires sudo.\n'
                              'put an entry in /etc/hosts with '
                              'the hostname and the host ip from ifconfig. '
                              'this is needed for lustre test setup llmount.sh'))
    parser.add_argument('-n', '--name',
                        help=('the hostname, this will be '
                              'the environment variable $HOSTNAME '
                              'by default.'))
    parser.add_argument('-m', '--mount',
                        help=('Requires sudo.\n'
                        'mount lustre of not already mounted '
                        'using lustre test setup llmount.sh'))
    parser.add_argument('-u', '--unmount',
                        help=('Requires sudo.\n'
                              'unmount lustre if mounted using '
                              'lustre test setup llmountcleanup.sh'))

    parser.add_argument('-r', '--remount')    
    
    

# the function that actually executes the command
# this function deals with the arguments after they are
# parsed and are made into a dictionary
def main(args):

    # if a host name is specified,
    # use it when setting the ip
    if args.get('set-ip'):
            if args.get('name'):
                set_ip(args['name'])
            else:
                set_ip()

   # if args.get('mount'):
   

    


if __name__ == '__main__':
    parser = set_up_parser()
    args = vars(parser.parse_args())
    main(args)
