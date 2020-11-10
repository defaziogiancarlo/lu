'''not a subcommand, not meant to be '''

import os
import re
import pathlib
import subprocess

import cfg
import lutils

def make_patch():

    version_pattern = r'(?P<kernel>[^_]*)(?:_\d)?\.[^\.]+$'
    
    lustre_path = lutils.find_lustre()

    # get kernel version
    version = subprocess.run(['uname', '-r'], capture_output=True,
                         check=True).stdout.decode().strip()    
    kv = re.match(version_pattern, version).group('kernel')

    # find the series file
    series_file_name = None
    with open(lustre_path / 'lustre/kernel_patches/which_patch', 'r') as f:
        for line in f.readlines():
            if kv in line:
                series_file_name = line.split()[0]
                
    # read the series file, and get full paths to each patch file
    series_path = lustre_path / 'lustre/kernel_patches/series' / series_file_name
    patch_files = None
    with open(series_path, 'r') as f:
        patch_dir = lustre_path / 'lustre/kernel_patches/patches'
        patch_files = [patch_dir / line.strip() for line in f.readlines()]


    home_dir = os.environ['HOME']
    rpm_src_patch = pathlib.Path(home_dir) / 'kernel/rpmbuild/SOURCES/patch-lustre.patch'
    with open(rpm_src_patch, 'w') as out_file:
        for patch_file in patch_files:
            text = None
            with open(patch_file, 'r') as in_file:
                text = in_file.read()
            out_file.write(text)
    

if __name__ == '__main__':
    make_patch()
    
    
    # find line in
    # lustre-release/lustre/kernel_patches/which_patch
    # with kernel release and then grab the patch series file name

    # grab all the file names for the patch series file
    # find all of the patch files
    # concatenate them into one file at
    # ~/kernel/rpmbuild/SOURCES/patch-lustre.patch
    
