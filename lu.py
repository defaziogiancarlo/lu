__doc__ = '''
Lustre Utilities - Scripts for Lustre development
'''

import argparse

import set_colors
import bashize
import lustre_paths

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='sub-command help', dest='subcommand')


parser_path = subparsers.add_parser('path', help=lustre_paths.parser_help)
lustre_paths.set_up_parser(parser_path)


if __name__ == '__main__':
    args = vars(parser.parse_args())
    print(args)
    subcommand = args.get('subcommand')

    if subcommand == 'path':
        lustre_paths.main(args)
