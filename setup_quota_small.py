import subprocess

import set_colors
import lustre_paths
import lustre_utils

# prerequisites:
# expects lustre installed using llmount.sh at /mnt/lustre

# get paths
lustre = str(lustre_paths.find_lustre())
lfs = str(lustre_paths.find_lustre(lr, 'lfs'))
lctl = str(lustre_paths.find_lustre(lr, 'lctl'))

# verify this is the right machine, slag3 by default
check_machine('slag3')

# make /mnt/lustre writeable
os.chmod('/mnt/lustre', 0777)

# set lustre debug logs to quotas
subprocess.run([lctl, 'set_param', 'debug=-1'],
               capture_output=True,
               check=True)
subprocess.run([lctl, 'set_param', 'subsytem_debug=-lquota'],
               capture_output=True,
               check=True)

# turn on quotas for osts and mdts
subprocess.run([lctl, 'conf_param', 'lustre.quota.ost=u'],
               capture_output=True,
               check=True)
subprocess.run([lctl, 'conf_param', 'lustre.quota.mdt=u'],
               capture_output=True,
               check=True)


# set 1 min grace period for block and inode for users
subprocess.run([lctl, 'conf_param', 'lustre.quota.mdt=u'],
               capture_output=True,
               check=True)


$LFS setquota -t -u --block-grace 20w4d12h3m13s --inode-grace 7200 /mnt/lustre

# set block limits for me
$LFS setquota -u defazio1 --block-softlimit 20M --block-hardlimit 30M /mnt/lustre

# set inode limits for me
$LFS setquota -u defazio1 --inode-softlimit 2048 --inode-hardlimit 3072 /mnt/lustre  
