import os
import csv
import argparse
import subprocess
from multiprocessing.dummy import Pool
#import asyncio
from glob import glob
import pandas as pd


POOL_SIZE = 48


def findBAMs(run):
    artic_path='ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_readMapping'
    test = os.path.join(run, artic_path, "*bam")
    return glob(test)


def parseCase(filepath):
    name = filepath.split('/')[-1]
    case = name.split('-')[0]
    return case


def createReport(run, bams):
    for i, bam in enumerate(bams):
        cov=bam.replace(".bam", "_coverage.txt")
        case=parseCase(bam)
        c = pd.read_csv(cov, sep="\t", header=None)
        c.columns=[0,1,2,3,4,5,6,7,8,case]
        index = c[0]+":"+c[1].astype(str)+"-"+c[2].astype(str)
        c=c.rename(index=index)
        this_case = c[[case]]
        if i==0:
            report = this_case
        else:
            report = pd.concat([report, this_case], axis=1)
    report.to_csv(os.path.join(run,"amplicon_coverage.csv"))


def runCoverage(bam):
    amplicon_bed='/fastdata/ncov2019-arctic/nCoV-2019/V3/nCoV-2019.insert.bed'
    outfile=bam.replace(".bam", "_coverage.txt")
    cov=open(outfile, "w")
    cmd='bedtools coverage -a %s -b %s' % (amplicon_bed, bam)
    #print(cmd)
    p = subprocess.Popen(cmd, shell=True, universal_newlines=True, stdout=cov)
    ret_code = p.wait()
    cov.flush()
    cov.close()
    return ret_code


def multithread(mymethod, poolsize, maplist):
    pool = Pool(poolsize)
    pool.map(mymethod, maplist)
    pool.close()
    pool.join()


if __name__ == "__main__":
    """
    Script to run coverage over all cases in alignment dir
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--run", nargs=1, type=str, help="full path to artice pipeline output folder", required=True)
    args = parser.parse_args()

    bam_map = findBAMs(args.run[0])
    multithread(runCoverage, POOL_SIZE, bam_map)
    createReport(args.run[0], bam_map)
