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
    the subprocess using \path.
    
