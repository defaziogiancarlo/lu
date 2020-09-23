__doc__ = '''
Lustre Utilities - Scripts for Lustre development
'''

#import argparse
#import set_colors
#import bashize
#import lustre_paths
import lu_parser




#parser = argparse.ArgumentParser()
#subparsers = parser.add_subparsers(help='sub-command help', dest='subcommand')


# lustre_paths

#def add_module_parser(module, subcommand_name, subparsers):
    
    













# set up the parser per the module being used
#parser_path = subparsers.add_parser('path', help=lustre_paths.parser_help)
#lustre_paths.set_up_parser(parser_path)


if __name__ == '__main__':
    parser = lu_parser.make_parser()
    #args = vars(parser.parse_args())
    args = parser.parse_args()
    args.func(vars(args))
 #   print(args)
 #   subcommand = args.get('subcommand')

 #   if subcommand == 'path':
 #       lustre_paths.main(args)
