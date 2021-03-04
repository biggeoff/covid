#!/usr/bin/python3

import pandas as pd
import argparse
import os
import sys


def loadDF(csv, heads=False):
    """ 
    load CSV into DF 
    default with no header
    return dataframe
    """
    try:
        if heads:
            df = pd.read_csv(csv)
        else:
            df = pd.read_csv(csv, header=None)
    except:
        print("Problem loading COG metadata file, ensure full path supplied with -c/--cog")
        sys.exit()
    return df


def prepareCog(df):
    """ 
    parse df down to ID and lineage 
    """
    cols=['sequence_name', 'country', 'adm1', 
        'pillar_2', 'sample_date', 'epi_week', 'lineage',
        'lineage_support', 'd614g', 'n439k', 'p323l', 'a222v',
        'y453f', 'e484k', 'n501y', 't1001i', 'p681h',
        'q27stop', 'del_21765_6']
    df.columns=cols
    df['COG_ID'] = df['sequence_name'].str.split('/').str[1]
    keep=['COG_ID', 'lineage']  
    df = df.reindex(columns=keep)
    return df


def preparePang(df):
    """ 
    parse df down to ID and lineage 
    """
    df['COG_ID'] = pang['taxon'].str.split('_').str[1].str.split('-').str[:-1].str.join('-')
    #fuck me that's a complicated line :-D
    keep=['COG_ID', 'lineage']  
    df = df.reindex(columns=keep)
    return df


def compareLineage(row, cog):
    """ 
    Cross reference row against COG-UK dataset 
    return True/False (str) and COG-UK lineage for reference 
    """
    print(row['COG_ID'])
    match = cog.loc[cog['COG_ID'] == row['COG_ID']]
    if match.size == 0:
        print("[{}] No Sample found in COG".format(row['COG_ID']))
        ret=pd.Series(["False", "NA"])
    elif match.iloc[0,1] == row['lineage']:
        print("[{}] LINEAGE MATCH!!".format(row['COG_ID']))
        ret=pd.Series(["True", match.iloc[0,1]])
    else:
        print("[{}] lineage doesn't match :o(".format(row['COG_ID']))
        ret=pd.Series(["False", match.iloc[0,1]])
    return ret


def printSummary(df):
    """ print counts of True/False """
    print("Matches = {}".format(pang[pang['cog_lineage'] == "True"].shape[0]))
    print("Errors = {}".format(pang[pang['cog_lineage'] == "False"].shape[0]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cog", nargs=1, type=str, help="full path to COG metadata download", required=True)
    parser.add_argument("-p", "--pangolin", nargs=1, type=str, help="full path to pangolin output", required=True)
    parser.add_argument("-o", "--output", nargs=1, type=str, help="full path to output results of the comparison to", required=True)
    args = parser.parse_args()

    cog = loadDF(args.cog[0], heads=False)
    pang = loadDF(args.pangolin[0], heads=True)

    #cog = loadDF("/home/geoffw/temp_cog/BRIS_cog_2021-02-25_metadata.csv")
    cog = prepareCog(cog)
    #rep='/largedata/share/MiSeqOutput2/210220_M03605_0235_000000000-JH7K2/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/lineage_report.csv'
    #pang = loadDF(rep, True)
    pang = preparePang(pang)
    pang[['cog_lineage', 'match']] = pang.apply(compareLineage, 1, args=(cog,))
    printSummary(pang)
    pang.to_csv(args.output[0])