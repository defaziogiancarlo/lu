'''
A wrapper around zdb to get files.
This is for getting lustre files
that aren't otherwise accesible while the file
system is mounted.
'''

import subprocess
import sys

def get_zdb_text(dataset, path):
    '''Get the output of zdb for path in dataset.'''
    text = subprocess.run(
        ['zdb', '-O', '-vvvvvv', str(dataset), str(path)],
        capture_output=True,
        check=True,
    )
    return text.stdout.decode()

#def key_value_line(line):



def parse_zdb(text):
    '''Turn the output of zdb into text so that
    a file can be copied.
    '''
    # the top section is a bunch of obj=* lines
    # look for line that says Indirect blocks
    in_blocks = False
    blocks = []
    for line in text.split('\n'):
        # #print(line)
        # if 'Indirect' not in line and not in_blocks:
        #     continue
        # if 'Indirect' in line:
        #     in_block = True
        #     continue
        # tokens = line.split()
        # print(line)
        # # get the lines with actual file data
        # if tokens[1] == 'L0':
        #     blocks.append(tokens[2])
        if 'L0' in line:
            tokens = line.split()
            blocks.append(tokens[2])
    return blocks


def copy_file(dataset, blocks, outfile):
    with open(outfile, 'wb') as f:
        for block in blocks:
            data = subprocess.run(
                ['zdb', '-R', dataset, block + ':r'],
                capture_output=True,
                check=True).stdout
            f.write(data)

def get_indirect_blocks():
    pass


def get_blocks(dataset, source):
    # sudo zdb -O -vvvvvv <dataset> <source>
    pass

def zbd_copy(dataset, source, dest):
    '''Copy file from zfs dataset using zdb.
    The file has location source within the dataset.
    It's contents are written to dest.
    '''
    pass
# first do dummy checks, make sure source file exists

if __name__ == '__main__':


    text = get_zdb_text(sys.argv[1], sys.argv[2])
    blocks = parse_zdb(text)
    print(blocks)
    print(len(blocks))
    copy_file(sys.argv[1], blocks, 'blocked_file')
