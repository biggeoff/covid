import os
import argparse
import pandas as pd


def loadLineage(lineagecsv):
    """ Read in lineage CSV output from Pangolin 
    Return pandas df with 3 useful columns renamed """
    df = pd.read_csv(lineagecsv)
    df['Sample Name'] = df['taxon'].str.split('_').str[1].str.split("-").str[0]
    df['Well'] = df['taxon'].str.split('_').str[1].str.split("-").str[1]
    df = df[['Well', 'Sample Name', 'lineage']]
    df.columns=['Well', 'Sample Name', r'Cт']
    return df


def parse2winpath(df):
    """ add columns required for winpath PCR upload 
    return df """
    cols=['Well', 'Sample Name', 'Target Name', 'Task', 
        'Reporter', 'Quencher', 'Cт', 'Cт Mean', 'Cт SD', 
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


def emitCSV(df):
    """ output parsed df and insert header above. """
    output_csv = "test.csv"
    df.to_csv(output_csv, header=None, index=False)
    header=["* Block Type = 96fast", "* Chemistry = TAQMAN",
        r'* Experiment File Name = D:\Users\INSTR-ADMIN\Documents\2019-nCoV\20200402_nCOV_SSIII_Run-02rpt_ABI-07_YD.eds',
        "* Experiment Run End Time = 2020-04-02 17:53:33 PM BST",
        "* Instrument Type = sds7500fast",
        "* Passive Reference =\n\n[Results]"
    ]
    with open(output_csv, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write('\n'.join(header) + '\n' + content)

    
if __name__ == "__main__":
    """
    Script to run coverage over all cases in alignment dir
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--lineage", nargs=1, type=str, help="full path to artice pipeline output folder", required=True)
    parser.add_argument("-o", "--output", nargs=1, type=str, help="output csv filename including full path", required=True)
    args = parser.parse_args()
    data = loadLineage(args.lineage[0])
    parsed = parse2winpath(data)
    emitCSV(parsed, args.output[0])