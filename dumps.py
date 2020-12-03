'''
Get the kernel dump from the dump file into a pandas dataframe.
'''

import datetime
import argparse
import re
import pandas as pd
import numpy as np
import pathlib

# show all the dataframe columns
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# grab a bunch of file names
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--paths', nargs='*',
                    help='the paths to all the kernel dump files')

# subsystems as defined by lustre in ~/lustre-release/lnet/include/uapi/linux/lnet/
# these are bits in luster
subsystem_names = [
    'undefined', 
    'mdc', 
    'mds', 
    'osc', 
    'ost', 
    'class', 
    'log', 
    'llite', 
    'rpc', 
    'mgmt', 
    'lnet', 
    'lnd', 
    'pinger', 
    'filter',
    'libcfs', 
    'echo', 
    'ldlm', 
    'lov', 
    'lquota', 
    'osd', 
    'lfsck',
    'snapshot', 
    '', 
    'lmv', 
    '', 
    'sec', 
    'gss', 
    '', 
    'mgc', 
    'mgs',
    'fid', 
    'fld',
]

# give each name a single bit and skip the empty string names
subsystems = {name : 2**i for i,name in enumerate(subsystem_names) if name}

# subsystemReStr   = r'(?P<subsystem>\d+)'
# debugMaskReStr   = r'(?P<debug_mask>\d+)'
# smpIDReStr       = r'(?P<smp_id>[\w\.]+)'
# timeReStr        = r'(?P<time>[\d\.]+)'
# stackSizeReStr   = r'(?P<stack_size>\d+)'
# pidReStr         = r'(?P<pid>\d+)'
# hostPidReStr     = r'(?P<host_pid>\d+)'
# srcLocationReStr = r'(?P<src_location>\S+\(\))'
# messageReStr     = r'(?P<message>.*)'

# debugLogLineReStr = (subsystemReStr + r':' +
#                      debugMaskReStr + r':' +
#                      smpIDReStr + r':' +
#                      timeReStr + r':' +
#                      stackSizeReStr + r':' +
#                      pidReStr + r':' +
#                      hostPidReStr + r':\(' +
#                      srcLocationReStr + r'\) ' +
#                      messageReStr)

#log_line_re = re.compile(debugLogLineReStr)

# ip addresses, nids, and messages
# a non-captuing group [0,255] allows leading zeroes, but no
# more that 3 digits
# IPoctetReStr    = `(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)`
# IPoctetDotReStr = `(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)`
# // <octet>.<octet>.<octet>.<octet>
# //IP4ReStr = IPoctetReStr + `\.` + IPoctetReStr + `\.` +
# //      IPoctetReStr + `\.` + IPoctetReStr
# IP4ReStr = IPoctetDotReStr + `{3}` + IPoctetReStr
# // lustre network ID <ip4>@<network>
# // <network> is "tcp" or "02ib" possibly followed by numbers
# NIDReStr    = `(?:` + IP4ReStr + `@` + `(?:tcp|o2ib)\d*` + `)`
# NIDReStrCap = `(?P<ip4>` + IP4ReStr + `)@` + `(?P<network>(?:tcp|o2ib)\d*)`

def log_to_field_strings(log):
    '''split a lustre debug log into a string for each field'''
    return log_line_re.match(log).groups()

#def log_to_fields():

def lustre_time_to_datetime(lustre_time):
    '''lustre is a string with format
    <sec>.<usec>'''
    datetime.datetime.fromtimestamp(float(lustre_time))
    
def file_to_dataframe(path, full_path=False):
    '''read a lustre kernel dump file into a pd
    dataframe'''
    # the same as the other regex, but without names
    log_line_re_nameless = (r'(\d+):(\d+):([\w\.]+):([\d\.]+):'
                            r'(\d+):(\d+):(\d+):\((\S+\(\))\) (.*)')
    #log_line_re_nameless = r'(\d+)'
    names = ['subsystem', 'debug_mask', 'smp_id',
             'time', 'stack_size', 'pid',
             'host_pid', 'src_location', 'message']
    #names = ['subsystem', ]
    types = {'subsystem'    : str, # np.uint32, # not used because converter is used
             'debug_mask'   : str, # np.uint32, # not used because converter is used
             'smp_id'       : str,
#             'time'         : np.float64,
             'stack_size'   : np.uint64,
             'pid'          : np.int32,
             'host_pid'     : np.int32,
             'src_location' : str,
             'message'      : str
    }
    # usecols is important to not use the entire match for a column value
    df = pd.read_csv(path,
                     # maybe faster than using the version with names?
                     sep=log_line_re_nameless, 
                     names=names,
                     # making this explicit
                     # used because of using regex for sep
                     engine='python',
                     # there's no index column in the logs, so add one
                     index_col=False,
                     # the logs have no header row
                     header=None,
                     # do type conversions
                     dtype=types,
                     # don't used the first column
                     #which is the entire regex match
                     usecols=list(range(1,len(names)+1)),
                     converters={
                         #'subsystem'  : (lambda x: int(x, 16)),
                         #'debug_mask' : (lambda x: int(x, 16)),
                         'time'       :
                         (lambda x: datetime.datetime.fromtimestamp(float(x))),
                     }
    )

    # convert columns to match lustre type
    # this should be in the constructor but I'm getting a warning
    # df = df.astype({'subsystem' : np.uint32, 'debug_mask' : np.uint32})
    # add filename
    # TODO this should get changed to node name maybe, or have node name and file name
    df['subsystem'].apply(int, base=16)
    df['subsystem'] = df['subsystem'].astype(np.uint32)
    df['debug_mask'].apply(int, base=16)
    df['debug_mask'] = df['debug_mask'].astype(np.uint32)    
    df["filename"] = path if full_path else pathlib.Path(path).name
    return df


def files_to_dataframe(paths):
    '''Turn multiple lustre kernel debug files into a big dataframe'''
    if not paths:
        return None
    # remove dupicates
    paths = list(dict.fromkeys(paths))
    return pd.concat(map(file_to_dataframe, paths))

# i think you can do (?i) within as expression to do a case insensitive match
def regex_search(df, regex_string, cols):
    '''find the rows that have a string that matches
    the given regex.'''
    # check if col is in df, and is string
    if isinstance(cols, str):
        cols = set([cols])
    else:
        cols = set(cols)
    # verify all col strings are in df
    if not set(df.columns).issuperset(cols):
        return None

    cols = list(cols)
    # could result in duplicate rows if multiple columns match the regex
    rdf = pd.concat(map(lambda x: df[df[x].str.contains(regex_string)], cols))
    return rdf.drop_duplicates()
    

        



if __name__ == '__main__':
    pass
    #jj = '00000400:02000000:25.0F:1598375394.790019:0:29281:0:(libcfs_cpu.c:1234:cfs_cpu_init()) HW NUMA nodes: 2, HW CPU cores: 32, npartitions: 2'
    #log_to_fields(jj)
    #df = file_to_dataframe('/g/g0/defazio1/tasks/2020_8__lnet_drops/toss-4887-dropped-lnet/dk.dmesg.copper31.1600728485')
#     paths_hard = ['/home/defazio1/lnet_logs/toss-4887-dropped-lnet/dk.dmesg.copper31.1600727112',
#                   '/home/defazio1/lnet_logs/zrelic5.lustre212.2020-09-21/dk.dmesg.zrelic5.1600728607']


# #    paths_hard = ['/home/defazio1/lnet_logs/toss-4887-dropped-lnet/test_copper31',
# #                  '/home/defazio1/lnet_logs/zrelic5.lustre212.2020-09-21/test_zrelic']
    
#     args = parser.parse_args()
#     paths = vars(args).get('paths')
#     if paths is None:
#         paths = paths_hard
    
#     #    df0 = file_to_dataframe(paths[0])
#     #    df1 = file_to_dataframe(paths[1])
#     print(paths)
    
#     df = files_to_dataframe(paths)

    #print(df)
    # with open('test_file', 'r') as f:
    #     for line in f:
    #         print(log_to_field_strings(line))
    
