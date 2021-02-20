import subprocess

import cfg

import path
import lutils


# prerequisites:
# expects lustre installed using llmount.sh at /mnt/lustre

# get paths
lustre = str(path.find_lustre())
lfs = str(path.find_lustre(lustre, 'lfs'))
lctl = str(path.find_lustre(lustre, 'lctl'))

# verify this is the right machine, slag3 by default
# check_machine('slag3')

# make /mnt/lustre writeable
os.chmod('/mnt/lustre', 0777)

# set lustre debug logs to quotas
subprocess.run([lctl, 'set_param', 'debug=-1'],
               stdout=subprocess.PIPE,
               check=True)
subprocess.run([lctl, 'set_param', 'subsytem_debug=-lquota'],
               stdout=subprocess.PIPE,
               check=True)

# turn on quotas for osts and mdts
subprocess.run([lctl, 'conf_param', 'lustre.quota.ost=u'],
               stdout=subprocess.PIPE,
               check=True)
subprocess.run([lctl, 'conf_param', 'lustre.quota.mdt=u'],
               stdout=subprocess.PIPE,
               check=True)


# set 1 min grace period for block and inode for users
subprocess.run([lctl, 'conf_param', 'lustre.quota.mdt=u'],
               stdout=subprocess.PIPE,
               check=True)


$LFS setquota -t -u --block-grace 20w4d12h3m13s --inode-grace 7200 /mnt/lustre

# set block limits for me
$LFS setquota -u defazio1 --block-softlimit 20M --block-hardlimit 30M /mnt/lustre

# set inode limits for me
$LFS setquota -u defazio1 --inode-softlimit 2048 --inode-hardlimit 3072 /mnt/lustre  
