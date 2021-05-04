from Bio import SeqIO
import pandas as pd
import argparse
import os


def parseID(row):
    """ parse ID from sample_name """
    return row['sample_name'].split('-')[0]


tailed="tailed_run_1/ncov2019-arctic-nf/tailedRun1.qc.csv"
untailed="untailed_runs_1_and_2/ncov2019-arctic-nf/untailedRun1and2.qc.csv"

t = pd.read_csv(tailed)
unt = pd.read_csv(untailed)

t['id'] = t.apply(parseID, 1)
unt['id'] = unt.apply(parseID, 1)

# 1. remove duplicates
t_u  = t.drop_duplicates(subset=['id'], keep='first')
unt_u = unt.drop_duplicates(subset=['id'], keep='first')

# 2. merge dataframes
merged  t_u.merge(unt_u, on="id", suffixes=('_tail','_untail'))

# 3. plot coverage? boxplot
