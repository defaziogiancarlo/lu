'''
Looks for objects with a trusted.fid xattr in
the zdb output.
'''
import subprocess
import sys

def get_trusted_fid_oids(dataset):
    p = subprocess.run(['zdb', '-dddd', dataset],
                       stdout=subprocess.PIPE).stdout.decode()

    last_oid = None
    trusted_fid_oids = []

    oid_next_line = False
    p = p.split('\n')
    for line in p:
        if oid_next_line:
            last_oid = line.strip().split()[0]
            oid_next_line = False
            continue
        if 'Object  lvl' in line:
            oid_next_line = True
            continue
        if 'trusted.fid' in line:
            trusted_fid_oids.append(last_oid)
    return trusted_fid_oids



if __name__ == '__main__':
    oids = get_trusted_fid_oids(sys.argv[1])
    print(oids)
