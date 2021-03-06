'''
Process the last_rcvd file in lustre
'''

import pathlib
import struct

import yaml

# from lustre/include/uapi/linux/lustre/lustre_disk.h
LR_EXPIRE_INTERVALS = 16
LR_SERVER_SIZE = 512
LR_CLIENT_START = 8192
LR_CLIENT_SIZE = 128

# The C code for this struct
# struct lr_server_data {
#   __u8  lsd_uuid[40];    /* server UUID */
#   __u64 lsd_last_transno;    /* last completed transaction ID */
#   __u64 lsd_compat14;    /* reserved - compat with old last_rcvd */
#   __u64 lsd_mount_count;     /* incarnation number */
#   __u32 lsd_feature_compat;  /* compatible feature flags */
#   __u32 lsd_feature_rocompat;/* read-only compatible feature flags */
#   __u32 lsd_feature_incompat;/* incompatible feature flags */
#   __u32 lsd_server_size;     /* size of server data area */
#   __u32 lsd_client_start;    /* start of per-client data area */
#   __u16 lsd_client_size;     /* size of per-client data area */
#   __u16 lsd_subdir_count;    /* number of subdirectories for objects */
#   __u64 lsd_catalog_oid;     /* recovery catalog object id */
#   __u32 lsd_catalog_ogen;    /* recovery catalog inode generation */
#   __u8  lsd_peeruuid[40];    /* UUID of MDS associated with this OST */
#   __u32 lsd_osd_index;     /* index number of OST in LOV */
#   __u32 lsd_padding1;    /* was lsd_mdt_index, unused in 2.4.0 */
#   __u32 lsd_start_epoch;     /* VBR: start epoch from last boot */
#   /** transaction values since lsd_trans_table_time */
#   __u64 lsd_trans_table[LR_EXPIRE_INTERVALS];
#   /** start point of transno table below */
#   __u32 lsd_trans_table_time; /* time of first slot in table above */
#   __u32 lsd_expire_intervals; /* LR_EXPIRE_INTERVALS */
#   __u8  lsd_padding[LR_SERVER_SIZE - 288];
# };

# this does not include the padding
# in the C code the padding size is determined using an int literal of 288
# but that 288 depends on LR_EXPIRE_INTERVALS, so it's dumb.
lr_server_data_format_list = [
    '<',   # little endian
    '40s', # __u8  lsd_uuid[40];    /* server UUID */
    'Q',   # __u64 lsd_last_transno;    /* last completed transaction ID */
    'Q',   # __u64 lsd_compat14;    /* reserved - compat with old last_rcvd */
    'Q',   # __u64 lsd_mount_count;     /* incarnation number */
    'I',   # __u32 lsd_feature_compat;  /* compatible feature flags */
    'I',   # __u32 lsd_feature_rocompat;/* read-only compatible feature flags */
    'I',   # __u32 lsd_feature_incompat;/* incompatible feature flags */
    'I',   # __u32 lsd_server_size;     /* size of server data area */
    'I',   # __u32 lsd_client_start;    /* start of per-client data area */
    'H',   # __u16 lsd_client_size;     /* size of per-client data area */
    'H',   # __u16 lsd_subdir_count;    /* number of subdirectories for objects */
    'Q',   # __u64 lsd_catalog_oid;     /* recovery catalog object id */
    'I',   # __u32 lsd_catalog_ogen;    /* recovery catalog inode generation */
    '40B', # __u8  lsd_peeruuid[40];    /* UUID of MDS associated with this OST */
    'I',   # __u32 lsd_osd_index;     /* index number of OST in LOV */
    'I',   # __u32 lsd_padding1;    /* was lsd_mdt_index, unused in 2.4.0 */
    'I',   # __u32 lsd_start_epoch;     /* VBR: start epoch from last boot */
           # /** transaction values since lsd_trans_table_time */
    str(LR_EXPIRE_INTERVALS) + 'Q', # __u64 lsd_trans_table[LR_EXPIRE_INTERVALS];
           # /** start point of transno table below */
    'I',      # __u32 lsd_trans_table_time; /* time of first slot in table above */
    'I',      # __u32 lsd_expire_intervals; /* LR_EXPIRE_INTERVALS */
]

lr_server_data_format = ''.join(lr_server_data_format_list)

# now add the padding to lr_server_format
padding_size = LR_SERVER_SIZE - struct.calcsize(lr_server_data_format)
lr_server_data_format_padded = lr_server_data_format + str(padding_size) + 'B'

server_names = [
    'uuid',
    'last_transno',
    'compat14',
    'mount_count'  ,
    'feature_compat' ,
    'feature_rocompat',
    'feature_incompat',
    'server_size',
    'client_start',
    'client_size',
    'subdir_count',
    'catalog_oid',
    'catalog_ogen',
    'peeruuid',
    'osd_index',
    'padding1',
    'start_epoch',
    'trans_table',
    'trans_table_time',
    'expire_intervals',
    'padding',
]

def read_server_data(b):
    '''Convert the server data from a struct to a
    dict.
    '''
    server_data = struct.unpack(lr_server_data_format_padded, b)
    x =  {n : d for n,d in zip(server_names, server_data)}
    x['uuid'] = x['uuid'].decode()
    return x
# client struct from the C code
# /* Data stored per client in the last_rcvd file. In le32 order. */
# struct lsd_client_data {
#   __u8  lcd_uuid[40];   /* client UUID */
#   __u64 lcd_last_transno;   /* last completed transaction ID */
#   __u64 lcd_last_xid;   /* xid for the last transaction */
#   __u32 lcd_last_result;    /* result from last RPC */
#   __u32 lcd_last_data;    /* per-op data (disposition for
#            * open &c.)
#            */
#   /* for MDS_CLOSE requests */
#   __u64 lcd_last_close_transno; /* last completed transaction ID */
#   __u64 lcd_last_close_xid; /* xid for the last transaction */
#   __u32 lcd_last_close_result;  /* result from last RPC */
#   __u32 lcd_last_close_data;  /* per-op data */
#   /* VBR: last versions */
#   __u64 lcd_pre_versions[4];
#   __u32 lcd_last_epoch;
#   /* generation counter of client slot in last_rcvd */
#   __u32 lcd_generation;
#   __u8  lcd_padding[LR_CLIENT_SIZE - 128];
# };

lsd_client_data_format_list = [
    '40s', # __u8  lcd_uuid[40];   /* client UUID */
    'Q',   # __u64 lcd_last_transno;   /* last completed transaction ID */
    'Q',   # __u64 lcd_last_xid;   /* xid for the last transaction */
    'I',   # __u32 lcd_last_result;    /* result from last RPC */
    'I',   # __u32 lcd_last_data;    /* per-op data (disposition for * open &c.) */
           # /* for MDS_CLOSE requests */
    'Q',   # __u64 lcd_last_close_transno; /* last completed transaction ID */
    'Q',   # __u64 lcd_last_close_xid; /* xid for the last transaction */
    'I',   # __u32 lcd_last_close_result;  /* result from last RPC */
    'I',   # __u32 lcd_last_close_data;  /* per-op data */
           # /* VBR: last versions */
    '4Q',  # __u64 lcd_pre_versions[4];
    'I',   # __u32 lcd_last_epoch;
           # /* generation counter of client slot in last_rcvd */
    'I',   # __u32 lcd_generation;
]

lsd_client_data_format = ''.join(lsd_client_data_format_list)

# now add the padding to lr_server_format
padding_size = LR_CLIENT_SIZE - struct.calcsize(lsd_client_data_format)
lsd_client_data_format_padded = lsd_client_data_format + str(padding_size) + 'B'

client_names = [
    'uuid',
    'last_transno',
    'last_xid',
    'last_result',
    'last_data',
    'last_close_transno',
    'last_close_xid',
    'last_close_result',
    'last_close_data',
    'pre_versions',
    'last_epoch',
    'generation',
    'padding',
]

def read_client_data(b):
    '''Convert the client data from a struct to a
    dict.
    '''
    client_data = struct.unpack(lsd_client_data_format_padded, b)
    return {n : d for n,d in zip(client_names, client_data)}

def read_clients_data(b):
    client_datas = struct.iter_unpack(lsd_client_data_format_padded, b)
    return [{n : d.decode() if n == 'uuid' else d for n,d in zip(client_names, client_data)} for client_data in client_datas]

def read_server_from_path(path):
    path = pathlib.Path(path)
    b = None
    with open(path, 'rb') as f:
        b = f.read()
    server = read_server_data(b[:LR_SERVER_SIZE])
    return server

def read_clients_from_path(path):
    path = pathlib.Path(path)
    b = None
    with open(path, 'rb') as f:
        b = f.read()
    clients = read_clients_data(b[LR_CLIENT_START:])
    return clients

def to_yaml(infile, outfile):
    '''Read in a last_rcvd file and output to yaml'''
    infile = pathlib.Path(infile)
    outfile = pathlib.Path(outfile)
    #    b = None
    #    with open(infile, 'rb') as f:
    #        b = f.read()
    server = read_server_from_path(infile)
    clients = read_clients_from_path(infile)
    clients.insert(0, server)
    with open(outfile, 'w') as f:
        #yaml.safe_dump(server, f, sort_keys=False)
        yaml.safe_dump(clients, f, sort_keys=False)

if __name__ == '__main__':
    to_yaml('/home/defazio1/last_rcvds/last_rcvd_saved_olaf', '/home/defazio1/last_rcvds/doodoo_olaf.yaml')
