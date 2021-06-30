'''
For old version of zdb,
get copy file by name.
'''

import re
import subprocess
import sys

block_number = r'\b[\da-f]+:[\da-f]+:[\da-f]+\b'
block_number_pat = re.compile(block_number)


def get_zdb_text(dataset, path):
    '''Get the output of zdb for path in dataset.'''

    # won't work right, but the object number should be
    # in the output
    text = subprocess.run(
        ['zdb', '-O', '-vvvvvv', str(dataset), str(path)],
        stdout=subprocess.PIPE,
#        check=True,
    ).stdout.decode().split('\n')

    # grab the object number
    object_id = None
    for line in text:
        if str(path) in line:
            tokens = line.split()
            object_id = tokens[0]
            break
    object_id = object_id.split('=')[1]
    print(object_id)

    text = subprocess.run(
        ['zdb', '-dddddd', str(dataset), object_id],
        stdout=subprocess.PIPE,
    ).stdout.decode().split('\n')

    return text

def get_blocks(text):

    blocks = []
    in_blocks = False
    for line in text:
        if not in_blocks:
            if 'Indirect' in line:
                in_blocks = True
        else:
            new_blocks = block_number_pat.findall(line)
            blocks += new_blocks
    return blocks

def copy_file(dataset, blocks, outfile):
    with open(outfile, 'wb') as f:
        for block in blocks:
            data = subprocess.run(
                ['zdb', '-R', dataset, block + ':r'],
                stdout=subprocess.PIPE,
                check=True).stdout
            f.write(data)

if __name__ == '__main__':
    text = get_zdb_text(sys.argv[1], sys.argv[2])
    blocks = get_blocks(text)
    print(blocks)
    copy_file(sys.argv[1], blocks, 'blocked_file')
