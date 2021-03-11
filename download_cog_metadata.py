#!/usr/bin/python3

import os
import subprocess
from glob import glob
import pandas as pd
import compare_df


def downloadMeta(outdir):
    """
    Pull latest metadata from CLIMB
    """
    cmd = 'scp climb-covid19-woodwardg@bham.covid19.climb.ac.uk'
    cmd += ':/cephfs/covid/bham/results/phylogenetics/latest/public/*_metadata.csv '+outdir
    subprocess.call(cmd, shell=True)


def loadMeta(outdir):
    """
    Load all CSV files in outdir
    return newest and previous as tuple
    """
    allmetas = glob(outdir+"cog*csv")
    new_file = allmetas[-1]
    previous_file = allmetas[-2]
    new = pd.read_csv(new_file)
    previous = pd.read_csv(previous_file)
    return new_file, new, previous


def loadSampleIDmap(f):
    """
    Load WinPath/CLIMB lookup table
    """
    df=pd.read_csv(f)
    df.columns=['winpath','cog']
    return df


def lookupWinpathID(row, lookup):
    """ 
    find Winpath ID from lookup 
    """
    match = lookup[lookup['cog'] == row['COG-UK_ID']]
    if match.size == 0:
        return "NA"
    else:
        return match.iloc[0,0] # winpath


def parseMeta(df, lookup):
    """ 
    PARSE:
     - rows with BRIS in sequence name
     - remove rest of info from sequence_name
     - add WinPathID
     - column with NEW/UPDATED/REMOVED
     - drop lineage_support column which causes mismatches
    """
    df = df[df.sequence_name.str.contains("BRIS")]
    df['COG-UK_ID'] = df['sequence_name'].str.split('/').str[1]
    df['Winpath_ID'] = df.apply(lookupWinpathID, 1, args=(lookup,))
    df = df.drop('lineage_support', 1)
    return df


def checkRowMatches(row, truth):
    """ 
    Return if pd.Series is NEW/STABLE/AMENDED
    between row and truth 
    """
    match = truth[truth['sequence_name'] == row['sequence_name']]
    if match.size == 0:
        status = "NEW"
    elif match.size > 0:
        if row.equals(match.iloc[0].squeeze()):
            status = "STABLE"
        else:
            status = "AMENDED"
    return status
        

def getDeletedRows(new, prev):
    """
    return rows in previous metadata 
    that are no longer in latest metadata 
    """
    unique = compare_df.getUniqueRecords(new, prev)
    deleted=unique[unique.Dataframe=="right_only"]
    deleted=deleted.drop('Dataframe', 1)
    deleted['STATUS'] = "DELETED"
    return deleted


if __name__ == "__main__":

meta_dir='/home/geoffw/temp_cog/'

downloadMeta(meta_dir)

newfile, new, prev = loadMeta(meta_dir)
lookup = loadSampleIDmap(os.path.join(meta_dir, "COGUK_ID_lookup.csv"))
new = parseMeta(new, lookup)
prev = parseMeta(prev, lookup)
new = new[new.sequence_name.str.contains("BRIS")]
prev = prev[prev.sequence_name.str.contains("BRIS")]

deleted = getDeletedRows(new, prev)
new['STATUS'] = new.apply(checkRowMatches, 1, args=(prev, ))
final = new.append(deleted)
final.to_csv(newfile.replace('.csv','_with_IDs.csv'), index=False)

final = createWinPathtemplate(newsamples)
copyToSampleNet(final)
