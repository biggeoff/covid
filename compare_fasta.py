from Bio import SeqIO
import pandas as pd
import argparse
import os


def loadMetadata():
    csv="full_case_details.csv"
    df = pd.read_csv(csv)
    return df


def loadFasta(fpath):
    fastas=[]
    for seq_record in SeqIO.parse(fpath, "fasta"):
        fastas.append(seq_record)
    return fastas


def calcPercent(x, y):
    return (x / y) * 100


def compareSeqIgnoreN(seq1, seq2):
    matches=0
    mismatches=0
    n=0
    for i, base in enumerate(seq1):
        if seq1[i] == "N" or seq2[i] == "N":
            n += 1
            continue
        elif seq1[i] == seq2[i]:
            matches += 1
        else:
            mismatches += 1
    
    print("Matches = %i mismatches = %i Ns = %i" % (matches, mismatches, n)) 
    pid = calcPercent(mismatches, len(seq1.seq))
    print("Percent identity =", 100 - pid, "%")
    return ( 100-pid )


def compareAll(row):
    if row['tailed_run'] == "na" or row['untailed93'] =="na":
        return
    t = os.path.join(t_path, row['tailed_run']+suffix)
    unt = os.path.join(unt_path, row['untailed93']+suffix)
    tailed=loadFasta(t)
    untailed=loadFasta(unt)
    pid = compareSeqIgnoreN(tailed[0], untailed[0])
    return pid


t_path = "tailed_run_1/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus"
unt_path = "untailed_runs_1_and_2/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus"
suffix = ".primertrimmed.consensus.fa"

if __name__ == "__main__":
    meta = loadMetadata()
    meta['tail_untail_identity'] = meta.apply(compareAll, 1)


