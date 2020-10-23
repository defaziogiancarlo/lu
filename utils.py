__doc__ = '''
Basic utilities
'''

import os

# some useful regexes
# a single ip4 octet 1,2,or 3 digits  0-255
ip4_octet_pattern_str = r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
# a single ip4 octet followed by a '.'
ip4_octet_dot_pattern_str = r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)'
# a full ip4 address  <octet>.<octet>.<octet>.<octet>
ip4_re_str = ip4_octet_dot_pattern_str + r'{3}' + ip4_octet_pattern_str



# printing in color
foreground = '\033[38;2;{r};{g};{b}m'
background = '\033[48;2;{r};{g};{b}m'

def set_foreground_rgb(r,g,b):
    print(foreground.format(r=r,g=g,b=b), end='')

def set_background_rgb(r,g,b):
    print(background.format(r=r,g=g,b=b), end='')

def reset_colors():
    print('\033[0m', end='')

def print_rgb(rgb, *args, **kwargs):
    set_foreground_rgb(*rgb)
    print(*args, **kwargs)
    reset_colors()


# who am I?
def check_machine(name):
    '''Check if the current is name.'''
    machine = os.environ['HOSTNAME']
    if machine != name:
        raise AssertionError(
            'Using the wrong machine, ' 
            'currently using {}, '
            'should be using {}.'.format(machine, name))








