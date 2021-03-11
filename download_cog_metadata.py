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


def parseNew2winpath(df):
    """ add columns required for winpath PCR upload 
    return df """
    df = df[df.STATUS.isin(['NEW', 'AMENDED'])]
    df = df.reset_index()
    df = df.drop('index',1)
    df = df[['COG-UK_ID', 'lineage']]
    df.columns=['Sample Name', u'C\u0442']

    cols=['Well', 'Sample Name', 'Target Name', 'Task', 
        'Reporter', 'Quencher', u'C\u0442', u'C\u0442 Mean', u'C\u0442 SD', 
        'Quantity', 'Quantity Mean', 'Quantity SD', 
        'Automatic Ct Threshold', 'Ct Threshold', 
        'Automatic Baseline', 'Baseline Start', 
        'Baseline End', 'Comments'
    ]
    df = df.reindex(columns=cols, fill_value='')
    df['row'] = (df.index // 8 % 8 + 1)
    df['col'] = (df.index % 12 + 1)
    df['row'] = df['row'].apply(lambda x: chr(ord('@')+x))
    df['Well']=df.row+df.col.astype(str)
    df = df.drop('row',1)
    df = df.drop('col',1)
    df['Baseline Start']=8
    df['Baseline End']=18
    df['Automatic Baseline']='FALSE'
    df['Ct Threshold']=df.index+40000
    df['Automatic Ct Threshold']='FALSE'
    df['Quencher']='None'
    df['Reporter']='FAM'
    df['Task']='UNKNOWN'
    df['Target Name']='COGUK'
    return df


def emitABItsv(df, outfile):
    """ output parsed df and insert header above. """
    df.to_csv(outfile, index=False, sep="\t", encoding='utf-8')
    header=["* Block Type = 96fast", "* Chemistry = TAQMAN",
        r'* Experiment File Name = D:\Users\INSTR-ADMIN\Documents\2019-nCoV\20200402_nCOV_SSIII_Run-02rpt_ABI-07_YD.eds',
        "* Experiment Run End Time = 2020-04-02 17:53:33 PM BST",
        "* Instrument Type = sds7500fast",
        "* Passive Reference =\n\n[Results]"
    ]
    with open(outfile, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write('\n'.join(header) + '\n' + content)

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

    abi = parseNew2winpath(final)
    emitABItsv(abi, newfile.replace('.csv','_for_ABI.tsv'))
    
    #copyToSampleNet(abi)
