## Autogenerated by lu ##
import argparse
import os
import pathlib
import subprocess
import sys

## Autogenerated by lu ##
# cfg will attempt to retrive a configuration
# file the first time it is imported
import cfg
import lutils

# default values
default_quota_vals = {
    'block_grace' : '20w4d12h3m13s',
    'inode_grace' : '7200',
    'block_softlimit' : '20M',
    'block_hardlimit' : '30M',
    'inode_softlimit' : '2048',
    'inode_hardlimit' : '3072',
}
## Autogenerated by lu ##
# the usage string for this command
# it will be used as the main usage string
# if this command is called directly,
# or as the subcommand help string if called indirecly by lu
# required for use by lu
parser_help = '''setup and check edquot feature for lfs'''

## Autogenerated by lu ##
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

## Autogenerated by lu ##
# set up the parser for this command
# the parser passed in is either one passed from
# lu, or one just created for this module
# part of all this infrastructure is to hopefully make
# it not matter what the context is, so this function
# can be written as if it's just for this module being
# called directly but it will work for lu as well
def set_up_parser_local(parser):
    pass

def setup_quota(fs_path='/mnt/lustre', user_name=None, **kwargs):
    '''set up lustre for quotas.'''

    if user_name is None:
        user_name = cfg.env.get('username')
    if user_name is None:
        sys.exit('ERROR: no username given or found in configuration file.')

    # use the default quota values unless some other value passed in
    quota_vals = {**default_quota_vals, **kwargs}

    # make the lustre file system writable
    mnt = pathlib.Path(fs_path)
    mnt.chmod(0o777)

    # find lctl
    lctl_path = str(lutils.find_lustre_path('lctl'))
    lfs_path = str(lutils.find_lustre_path('lfs'))

    # set up logging for quotas
    subprocess.run([lctl_path, 'set_param', 'debug=-1'])
    subprocess.run([lctl_path, 'set_param', 'subsystem_debug=lquota'])

    # turn on quotas for osts and mdts for users
    subprocess.run([lctl_path, 'conf_param', 'lustre.quota.ost=u'])
    subprocess.run([lctl_path, 'conf_param', 'lustre.quota.mdt=u'])

    # set grace periods for block and inode for users
    subprocess.run([lfs_path, 'setquota', '-t', '-u', 
                    '--block-grace', quota_vals['block_grace'],
                    '--inode-grace', quota_vals['inode_grace'], 
                    fs_path])    

    # set block limits for the user
    subprocess.run([lfs_path, 'setquota', '-u', user_name, 
                    '--block-softlimit', quota_vals['block_softlimit'],
                    '--block-hardlimit', quota_vals['block_hardlimit'],
                    fs_path])
    subprocess.run([lfs_path, 'setquota', '-u', user_name, 
                    '--inode-softlimit', quota_vals['inode_softlimit'],
                    '--inode-hardlimit', quota_vals['inode_hardlimit'],
                    fs_path])


def setup_test(reset=False):
    '''build lustre, mount lustre, make file system writeable, give myself a quota.
    if just doing a reset, first unmount, only call make when building, don't need to set the
    ip'''
    if reset:
        lutils.unmount_lustre()
    if reset:
        lutils.build_lustre(full=False)
    else:
        lutils.build_lustre(full=True)
    if not reset:
        lutils.set_ip()
    lutils.mount_lustre()
    setup_quota()


def check_under_quota(fs_path='/mnt/lustre'):
    '''see if correct output for lfs'''
        
    lfs_path = str(lutils.find_lustre_path('lfs'))
    user_name = cfg.env.get('username')
    quota_status = subprocess.run([lfs_path, 'quota', '-e', 
                                   '-u', user_name, fs_path],
                                  stdout=subprocess.PIPE, 
                                  check=True).stdout.decode().strip()
    expected_status = f'{user_name} under quota on {fs_path}'
    if quota_status != expected_status:
        print('unexpected quota status:\n'
              f'expected: {expected_status}\nactual: {quota_status}',
              file=sys.stderr)


def write_to_lustre(n, fs_path='/mnt/lustre', filename='random_bytes_test'):
    '''write a n random bytes to a file'''
    output_file = pathlib.Path(fs_path) / filename

    # don't write negative length
    if n < 0:
        sys.exit(f'Can\'t write negative number of bytes {n} to {output_file}')

    with open(output_file, 'wb') as f:
        f.write(os.urandom(n))
        

def check_over_quota(fs_path='/mnt/lustre'):
    '''see if correct output for lfs'''
        
    lfs_path = str(lutils.find_lustre_path('lfs'))
    user_name = cfg.env.get('username')
    quota_status = subprocess.run([lfs_path, 'quota', '-e', 
                                   '-u', user_name, fs_path],
                                  stdout=subprocess.PIPE, 
                                  check=True).stdout.decode().strip()
    expected_status = f'{user_name} under quota on {fs_path}'
    if quota_status != expected_status:
        print('unexpected quota status:\n'
              f'expected: {expected_status}\nactual: {quota_status}',
              file=sys.stderr)
    

def get_pools(prefixed=False, fs_name='lustre'):
    '''get the pools in a file system,
    returns a list of their names without 
    <filesystem>. prepended, unless prefixed=True'''
    pools = subprocess.run([lctl_path, 'pool_list', fs_name],
                           stdout=subprocess.PIPE, 
                           check=True,).stdout.decode().splitlines()[1:]

    # the filesystem name is kept as a prefix
    if prefixed:
        return pools

    # the filesytem prefix is removed
    return [pool.split('.')[0] for pool in pools]


def get_pool_osts(pool_name, filesystem='lustre', full_name=False):
    '''get the OSTs in a pool, returns a list of numbers,
    or if full_name=True, return full name given by lctl'''
    # check if the pool name is prefixed by a file system name
    # if not, prepend it
    # just check for a '.'
    # TODO use regex, need to know filesystem
    if '.' not in pool_name:
        pool_name = filesystem + '.' + pool_name

    osts = subprocess.run([lctl_path, 'pool_list', pool_name],
                           stdout=subprocess.PIPE, 
                           check=True,).stdout.decode().splitlines()[1:]

    # the names given by lctl
    if full_name:
        return osts

    # dig out the number
    ost_name_pattern = r'[\w]+-OST(?P<number>[\da-fA-F]{4})_UUID'
    ost_name_re = re.compile(ost_name_pattern)
    # OST number are hexadecimal
    ost_nums = []
    for ost in osts:
        num_string = ost_name_re.fullmatch(ost).group('number')
        ost_nums.append(int(num_string, 16))
    return ost_nums


def setup_pools(fs_path='/mnt/lustre'):
    ''' create an ost pool, and set quota on it'''
    # create a pool for each OST, there should be 0 and 1
    lctl_path = str(lutils.find_lustre_path('lctl'))
    lfs_path = str(lutils.find_lustre_path('lfs'))

    pool0_name = 'pool0'
    pool1_name = 'pool1'

    subprocess.run([lctl_path, 'pool_new', 'lustre.' + pool0_name],
                   check=True)
    subprocess.run([lctl_path, 'pool_new', 'lustre.' + pool1_name],
                   check=True)

    # now verify the pools exist, the 2nd and 3rd lines
    # should just be the pools names
    pools = subprocess.run([lctl_path, 'pool_list', 'lustre'],
                           stdout=subprocess.PIPE, 
                           check=True,).stdout.decode().splitlines()[1:]
    if pools == []:
        sys.exit('failed to create pools')

    if pools[0] != ('lustre.' + pool0_name) or pools[1] != ('lustre.' + pool1_name):
        sys.exit('wrong pools created')

    # now associate each pool with an OST
    subprocess.run([lctl_path, 'pool_add', 'lustre.' + pool0_name, 'OST[0]'],
                   check=True)
    subprocess.run([lctl_path, 'pool_add', 'lustre.' + pool1_name, 'OST[1]'],
                   check=True)

    # check that OST added
    osts = subprocess.run([lctl_path, 'pool_list', 'lustre.' + pool0_name],
                           stdout=subprocess.PIPE, 
                           check=True,).stdout.decode().splitlines()[1:]
    # should be just OST 0
    if osts[0] != 'lustre-OST0000_UUID':
        sys.exit('failed to add OST to pool')

    # check that OST added
    osts = subprocess.run([lctl_path, 'pool_list', 'lustre.' + pool1_name],
                           stdout=subprocess.PIPE, 
                           check=True,).stdout.decode().splitlines()[1:]
    # should be just OST 1
    if osts[0] != 'lustre-OST0001_UUID':
        sys.exit('failed to add OST to pool')

    # now create a file for each pool
    # now associate each pool with an OST
    pool0_filename = pathlib.Path(fs_path) / 'pool0_file'
    subprocess.run([lfs_path, 'setstripe', '--pool', pool0_name, pool0_filename],
                   check=True)
    pool1_filename = pathlib.Path(fs_path) / 'pool1_file'
    subprocess.run([lfs_path, 'setstripe', '--pool', pool1_name, pool1_filename],
                   check=True)

    
def remove_pools(filesystem='lustre'):

    lctl_path = str(lutils.find_lustre_path('lctl'))
    lfs_path = str(lutils.find_lustre_path('lfs'))

    fs_path = pathlib.Path('/mnt') / filesystem

    # delete everything in /mnt/<filesystem>
    lutils.remove_dir_contens(fs_path)
    
    # find all pools, and all OSTs in each pool
    # and remove all OSTs
    pools = get_pools(prefixed=True)
    for pool in pools:
        osts = get_pool_osts(pool)
        ost_string = 'OST[' + ','.join(map(str,osts)) + ']'
        subprocess.run([lctl_path, 'pool_remove', 
                        pool, ost_string], check=True)

    # destroy the pools
    for pool in pools:
        subprocess.run([lctl_path, 'pool_destroy', pool],
                       check=True)


    
def check_over_quota_pool():
    pass

def check_under_quota_pool():
    pass





def test_edquot():
    '''set up quotas, then check how the edquot stuff works'''
    # build and  mount lustre
    # setup user to have access to lustre, and a quota
    # check if edquot give the right results
    pass


def test_sanity_quota(filename):
    '''Use a test in sanity_quota.sh
    to create quota logs'''

    # if filename not absolute, put into homedir
    p = pathlib.Path(filename)
    if not p.is_absolute():
        p = pathlib.Path(cfg.env['user_home']) / p
    
    lctl_path = str(lutils.find_lustre_path('lctl'))

    # set the logs to just quota
    subprocess.run([lctl_path, 'debug_kernel', '/dev/null'],
                   check=True)
    
    # set up logging for quotas
    subprocess.run([lctl_path, 'set_param', 'debug=-1'],
                   check=True)

    subprocess.run([lctl_path, 'set_param', 'subsystem_debug=lquota'],
                   check=True)


    # clear the debug log
    subprocess.run([lctl_path, 'debug_kernel', '/dev/null'],
                   check=True)


    # run auster for my test
    auster_path = str(lutils.find_lustre_path('auster'))
    subprocess.run([auster_path, 'sanity-quota', '--only', '1b2'],
                   check=True)

    # dump logs to filename
    subprocess.run([lctl_path, 'debug_kernel', p], check=True)
    


## Autogenerated by lu ##
# the function that actually executes the command
# this function deals with the arguments after they are
# parsed and are made into a dictionary
def main(args):
    #setup_test(reset=True)
    #check_e_flag()
    #setup_quota()
    #check_under_quota()
    #write_to_lustre(666)
    #setup_test()
    #setup_pools()
    test_sanity_quota('edquot_logs')

## Autogenerated by lu ##
if __name__ == '__main__':
    parser = set_up_parser()
    args = vars(parser.parse_args())
    main(args)
