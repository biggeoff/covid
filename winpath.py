import os
import argparse
import pandas as pd


def loadLineage(lineagecsv):
    """ Read in lineage CSV output from Pangolin 
    Return pandas df with 3 useful columns renamed """
    df = pd.read_csv(lineagecsv)
    df['COG_ID'] = df['taxon'].str.split('_').str[1].str.split("-").str[:-1].str.join('-')
    df['Well'] = df['taxon'].str.split('_').str[1].str.split("-").str[2]
    df = df[['Well', 'COG_ID', 'lineage']]
    df.loc[df['lineage']=='None', 'lineage'] = "" # leave blank so can be assigned in WinPath later
    df.columns=['Well', 'COG_ID', u'C\u0442']
    return df


def parse2winpath(lineage, ss):
    """ 
    refactor SampleSheet dataframe
    merge with lineage report
    add columns required for winpath PCR upload 
    return df 
    """
    ss = ss.reindex(columns=["Sample_ID", "Column1"])
    df = pd.merge(left=lineage, right=ss, left_on="COG_ID", right_on="Sample_ID")
    df.columns=['Well', 'COG_ID', u'C\u0442', 'Sample_ID', 'Sample Name']
    
    cols=['Well', 'Sample Name', 'Target Name', 'Task', 
        'Reporter', 'Quencher', u'C\u0442', u'C\u0442 Mean', u'C\u0442 SD', 
        'Quantity', 'Quantity Mean', 'Quantity SD', 
        'Automatic Ct Threshold', 'Ct Threshold', 
        'Automatic Baseline', 'Baseline Start', 
        'Baseline End', 'Comments'
    ]
    df = df.reindex(columns=cols, fill_value='')
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


def emitCSV(df, outfile):
    """ output parsed df and insert header above. """
    #output_csv = "test.csv"
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

    
def lineage2ABI(ss, run, worklist):
    """
    Script to run coverage over all cases in alignment dir
    """
    lineage = os.path.join(run, worklist+"_lineage_report.csv")
    output = os.path.join(run, worklist+"_ABI_local.txt")
    data = loadLineage(lineage)
    parsed = parse2winpath(data, ss)
    emitCSV(parsed, output)