#!/usr/bin/python3

import pandas as pd
import argparse
import os
import sys


def loadDF(csv, cols=None):
    """ load CSV into DF 
    default with no header
    return dataframe
    """
    try:
        df = pd.read_csv(csv, header=cols)
    except:
        print("Problem loading COG metadata file, ensure full path supplied with -c/--cog")
        sys.exit()
    return df

def prepareCOG(df)
    cols=['sequence_name', 'country', 'adm1', 
        'pillar_2', 'sample_date', 'epi_week', 'lineage',
        'lineage_support', 'd614g', 'n439k', 'p323l', 'a222v',
        'y453f', 'e484k', 'n501y', 't1001i', 'p681h',
        'q27stop', 'del_21765_6']
    df.columns=cols
    #sort out which columns are needed
    df = df.reindex(columns=cols, fill_value='')
    return df

#if __name__ == "__main__":
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--cog", nargs=1, type=str, help="full path to COG metadata download", required=True)
parser.add_argument("-p", "--pangolin", nargs=1, type=str, help="full path to pangolin output", required=True)
args = parser.parse_args()

cog = loadDF(args.cog)
pang = loadDF(args.pangolin)

