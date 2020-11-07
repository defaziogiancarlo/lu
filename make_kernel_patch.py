'''not a subcommand, not meant to be '''

import re
import subprocess

import cfg
import lutils

def make_patch():

    version_pattern = r'(?P<kernel>.*)\.[^\.]+$'
    
    lustre_path = lutils.find_lustre()

    # get kernel version
    version = subprocess.run(['uname', '-r'], capture_output=True,
                         check=True).stdout.decode().strip()    
    kv = re.match(version_pattern, version).group('kernel')

    # find the series file
    series_file_name = None
    with open(lustre_path / 'lustre/kernel_patches/which_patch', 'r') as f:
        for line in f.lines():
            if kv in line:
                series_file_name = line.split()[0]

    # read the series file, and get full paths to each patch file
    series_path = lustre_path / 'lustre/kernel_patches' / series_file_name
    patch_files = None
    with open(seried_path, 'r') as f:
        patch_dir = lustre_path / 'kernel_patches/patches'
        patch_file_lines = f.lines()
        patch_files = [path_dir / line for line in patch_file_lines]

    
    

if __name__ == '__main__':
    make_patch()
    
    
    # find line in
    # lustre-release/lustre/kernel_patches/which_patch
    # with kernel release and then grab the patch series file name

    # grab all the file names for the patch series file
    # find all of the patch files
    # concatenate them into one file at
    # ~/kernel/rpmbuild/SOURCES/patch-lustre.patch
    
