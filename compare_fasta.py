from Bio import SeqIO
import pandas as pd
import argparse
import os
import glob


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
        if i > 29901:
            continue
        elif seq1[i] == "N" or seq2[i] == "N":
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
    os.chdir("/mnt/NGS_DATA_at_Bristol/COVID/")
    meta = loadMetadata()
    meta['tail_untail_identity'] = meta.apply(compareAll, 1)


'''
#######################
# 4 mismatches
#######################

#BRIS-25CE90	4-20V00335709  - swap
#BRIS-25CF06	4-20V00335821 - swap

#BRIS-1855B5B	20V60165216
#BRIS-1856659    20V60170512
#BRIS-25CF06     20V00335821
#BRIS-25AC4D     20V60171170


#####################################################
# failed because they're too different!!! bad sign!
#####################################################
cogs=['BRIS-1855B5B', 'BRIS-1856659','BRIS-25CF06', 'BRIS-25AC4D']
wins=['20V60165216','20V60170512','20V00335821','20V60171170']

root='/mnt/NGS_DATA_at_Bristol/COVID'
test_n='/tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus'
truth_n='/verification/96plate_validation/'
for i, cog in enumerate(cogs):
    truth=glob.glob(root+truth_n+cogs[i]+"*")
    tr=loadFasta(truth[0])
    test_reps=glob.glob(root+test_n+"/*"+wins[i]+"*")
    for testr in test_reps:
        print("Testing:\n \t{} [{}] and \n\t{} [{}]".format(
            testr.split('/')[-1],
            len(te[0].seq),
            truth[0].split('/')[-1],
            len(tr[0].seq)
            )
        )
        te=loadFasta(testr)
        compareSeqIgnoreN(tr[0], te[0])
        print("=======================")
'''

'''
########################################
# Needle far too slow....
########################################
from Bio.Emboss.Applications import NeedleCommandline
needle_align_code(tr[0].seq, te[0].seq)
#extremely slow
def needle_align_code(query_seq, target_seq):
    needle_cline = NeedleCommandline(asequence="asis:" + query_seq,
                                     bsequence="asis:" + target_seq,
                                     aformat="simple",
                                     gapopen=10,
                                     gapextend=0.5,
                                     outfile='stdout'
                                     )
    out_data, err = needle_cline()
    out_split = out_data.split("\n")
    p = re.compile("\((.*)\)")
    return p.search(out_split[25]).group(1).replace("%", "")




############################
# Pairwise2 doesn't ignore Ns
############################
from Bio import pairwise2
global_align = pairwise2.align.globalxx(tr[0].seq, te[0].seq)

'''

'''
cogs=['BRIS-1855B5B', 'BRIS-1856659',, 'BRIS-25AC4D']
wins=['20V60165216','20V60170512','','20V60171170']
sudo bash
cat verification/96plate_validation/BRIS-1855B5B* \
verification/96plate_validation/BRIS-1856659* \ 
verification/96plate_validation/BRIS-25CF06* \
verification/96plate_validation/BRIS-25AC4D* > expected.fa

cat tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*20V60165216* > 20V60165216.all.fa
cat tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*20V60170512* > 20V60170512.all.fa
cat tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*20V00335821* > 20V00335821.all.fa
cat tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*20V60171170* > 20V60171170.all.fa

cat *.fa > follow_up.fa

#SWAPPED:
cat verification/96plate_validation/BRIS-25CF06* > sample_swap_investigation.fa
cat tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*20V00335709* >> sample_swap_investigation.fa
cat verification/96plate_validation/BRIS-25CE90* >> sample_swap_investigation.fa
cat tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*20V00335821* >> sample_swap_investigation.fa

#Other 4:
cat verification/96plate_validation/BRIS-1855B5B* > BRIS-1855B5B_investigation.fa
cat tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*20V60165216* >> BRIS-1855B5B_investigation.fa
cat verification/96plate_validation/BRIS-1856659* > BRIS-1856659_investigation.fa
cat tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*20V60170512* >> BRIS-1856659_investigation.fa
cat verification/96plate_validation/BRIS-1855845* > BRIS-1855845_investigation.fa
cat tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*20V00299373* >> BRIS-1855845_investigation.fa
cat verification/96plate_validation/BRIS-25AC4D* > BRIS-25AC4D_investigation.fa
cat tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*20V60171170* >> BRIS-25AC4D_investigation.fa

uploaded to: https://clades.nextstrain.org/

'''
