__doc__ = '''
set terminal colors persistently or just print
something with colors set.'''

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

