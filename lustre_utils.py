__doc__ = '''
Basic utilities
'''

import os

def check_machine(name):
    '''Check if the current machine is what
    you think it is.'''
    machine = os.environ['HOSTNAME']
    if machine != name:
        raise AssertionError(
            'Using the wrong machine, ' 
            'currently using {}, '
            'should be using {}.'.format(machine, name))



