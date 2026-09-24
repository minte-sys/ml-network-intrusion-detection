from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ['duration','protocol_type','service','flag','src_bytes','dst_bytes','land','wrong_fragment','urgent','hot','num_failed_logins','logged_in','num_compromised','root_shell','su_attempted','num_root','num_file_creations','num_shells','num_access_files','num_outbound_cmds','is_host_login','is_guest_login','count','srv_count','serror_rate','srv_serror_rate','rerror_rate','srv_rerror_rate','same_srv_rate','diff_srv_rate','srv_diff_host_rate','dst_host_count','dst_host_srv_count','dst_host_same_srv_rate','dst_host_diff_srv_rate','dst_host_same_src_port_rate','dst_host_srv_diff_host_rate','dst_host_serror_rate','dst_host_srv_serror_rate','dst_host_rerror_rate','dst_host_srv_rerror_rate']
CATEGORIES = ['protocol_type','service','flag']
NUMERIC = [x for x in FEATURES if x not in CATEGORIES]

def read_dataset(path):
    df = pd.read_csv(path, header=None, names=FEATURES+['attack_type','difficulty'])
    if df.shape[1] != 43: raise ValueError('Expected 43 NSL-KDD columns')
    return df

def validate_frame(df, max_rows=None):
    missing = sorted(set(FEATURES)-set(df.columns))
    if missing: raise ValueError('Missing columns: '+', '.join(missing))
    if not len(df): raise ValueError('CSV has no records')
    if max_rows is not None and len(df)>max_rows: raise ValueError('Maximum 10,000 records per upload')
    df = df[FEATURES].copy()
    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors='raise')
    for col in CATEGORIES:
        df[col] = df[col].astype('string').fillna('missing').astype(str)
    return df
