__doc__ = '''
Create a bash script with at the path given by the user.
Prepend the line #!/bin/bash and make executable.
Find the correct location of bash if not /bin/bash.
If the file already begins with '#!' or is not a normal
file, make no changes to it.
'''

import pathlib
import shutil
import subprocess
import sys
import uuid

# could deal with race conditions if you
# really like pain, make an atomic file modification
# function
def bashize(path):
    '''Create a bash script at the given path.
    If no file exists, create one.
    If a file does exist but does not start with
    #!, add #!/bin/bash and make executable,
    if #! already exists, do nothing.
    '''
    path = pathlib.Path(path)

    # get bash's path
    which_bash_path = subprocess.run(['which', 'bash'],
                                     capture_output=True,
                                     check=True)
    shebangbash = '#!' + which_bash_path.stdout.decode() + '\n'

    # ensure something exists at path
    path.touch()

    # is path is something besides a normal file, don't mess with it
    if not path.is_file():
        raise FileNotFoundError(str(path) + ' is not normal a'
                                    ' normal file, cannot bashize')

    # check if #! line already exists
    # in which case there's nothing to do
    with open(path, 'rb') as f:
        first_2 = f.read(2)
        if first_2 == b'#!':
            print(str(path) + ' already starts with \'!#',
                  file=sys.stderr)
            return

    # make new file
    current_text = path.read_text()
    f_name = pathlib.Path(str(uuid.uuid4()))
    with open(f_name, 'w') as f:
        f.write(shebangbash)
        f.write(current_text)

    # overwrite and set permisssions
    shutil.move(f_name, path)
    path.chmod(0o744)
