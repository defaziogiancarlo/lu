import lustre_paths
import subprocess
import argparse





def main(filename):
    '''Simple wrapper around lustre's version
    of checkpatch.pl'''
    lustre = lustre_paths.find_lustre()
    checkpatch = lustre_paths.find_path('checkpatch')
    if checkpath is not None:
        subprocess.run([checkpatch, filename],
                       stdout=subprocess.PIPE,
                       check=True)

if __name__ == '__main__':
    
