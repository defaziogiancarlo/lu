'''
Process the last_rcvd file in lustre
'''

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
    '40B', # __u8  lsd_uuid[40];    /* server UUID */
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
    'lsd_uuid',
    'lsd_last_transno',
    'lsd_compat14',
    'lsd_mount_count'  ,
    'lsd_feature_compat' ,
    'lsd_feature_rocompat',
    'lsd_feature_incompat',
    'lsd_server_size',
    'lsd_client_start',
    'lsd_client_size',
    'lsd_subdir_count',
    'lsd_catalog_oid',
    'lsd_catalog_ogen',
    'lsd_peeruuid',
    'lsd_osd_index',
    'lsd_padding1',
    'lsd_start_epoch',
    'lsd_trans_table',
    'lsd_trans_table_time',
    'lsd_expire_intervals',
    'lsd_padding',
]

def read_server_data(b):
    '''Convert the server data from a struct to a
    dict.
    '''
    server_data = struct.unpack(b)
    return {n : d for n,d in zip(server_names, server_data)}

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
    '40B', # __u8  lcd_uuid[40];   /* client UUID */
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
    'lcd_uuid',
    'lcd_last_transno',
    'lcd_last_xid',
    'lcd_last_result',
    'lcd_last_data',
    'lcd_last_close_transno',
    'lcd_last_close_xid',
    'lcd_last_close_result',
    'lcd_last_close_data',
    'lcd_pre_versions',
    'lcd_last_epoch',
    'lcd_generation',
    'lcd_padding',
]

def read_client_data(b):
    '''Convert the client data from a struct to a
    dict.
    '''
    client_data = struct.unpack(b)
    return {n : d for n,d in zip(client_names, client_data)}
