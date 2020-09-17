__doc__ = '''
Basic utilities
'''
import os
import subprocess

def check_machine(name):
    '''Check if the current machine is what
    you think it is.'''
    machine = os.environ['HOSTNAME']
    if machine != name:
        raise AssertionError(
            'Using the wrong machine, ' 
            'currently using {}, '
            'should be using {}.'.format(machine, name))

def make_subprocess_command(path):
    '''make a function that will attemp to run
    the subprocess using \path.'''
    pass

def add_module_parser(module_name, subcommand_name, subparsers):
    '''Add the parser of a module to the main parser.'''
    # create a subparser attached to subparsers
    module_parser = subparsers.add_parser(subcommand_name,
                                          help=module_name.parser_help)
    module_name.set_up_parser(module_parser)


