__doc__ = '''
Lustre Utilities - Scripts for Lustre development
'''

import argparse

parser = argparse.ArgumentParser()
#parser.add_argument('boner')
subparsers = parser.add_subparsers(help='sub-command help')
parser_a = subparsers.add_parser('a', help='a help')
parser_a.add_argument('bar', type=int, help='bar help')
parser_b = subparsers.add_parser('b', help='b help')
parser_b.add_argument('--baz', choices='XYZ', help='baz help')


if __name__ == '__main__':
    args = parser.parse_args()

