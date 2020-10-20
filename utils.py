__doc__ = '''
Basic utilities
'''

import os

ip4_octet_pattern_str = r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
ip4_octet_dot_pattern_str = r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)'
ip4_re_str = ip4_octet_dot_pattern_str + r'{3}' + ip4_octet_pattern_str

def check_machine(name):
    '''Check if the current machine is what
    you think it is.'''
    machine = os.environ['HOSTNAME']
    if machine != name:
        raise AssertionError(
            'Using the wrong machine, ' 
            'currently using {}, '
            'should be using {}.'.format(machine, name))



