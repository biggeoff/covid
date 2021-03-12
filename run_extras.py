import os
import subprocess
from multiprocessing.dummy import Pool
import argparse
import pandas as pd


def getBamMap(run_dir):
    bams=[]
    files = os.listdir(run_dir)
    for bam in [f for f in files if f.endswith(".bam")]:
        case = "-".join(bam.split("-")[:-1])
        bams.append((case, bam, run_dir))
    return bams


def getFaMap(run_dir):
    fas=[]
    files = os.listdir(run_dir)
    for fa in [f for f in files if f.endswith(".fa")]:
        case = "-".join(fa.split("-")[:-1])
        fas.append((case, fa, run_dir))
    return fas

def runNextClade(row):
    case, fa, run_dir = row
    cmd = 'sudo docker run --rm '
    cmd += '-v '+run_dir+'/ncovIllumina_sequenceAnalysis_makeConsensus/:/in/ '
    cmd += '-v '+run_dir+'/nextclade/:/out/ '
    cmd += 'nextstrain/nextclade nextclade '
    cmd += '-i /in/'+fa+' '
    cmd += '-o /out/'+case+'_nextclade.json '
    print("processing {}".format(case))
    subprocess.run(cmd, shell=True)


def runPicard(row):
    case, bam, run_dir = row
    cmd= "sudo docker run --rm "
    cmd += "-v "+run_dir+"/ncovIllumina_sequenceAnalysis_readMapping/:/in/ "
    cmd += "-v "+run_dir+"/picard/:/out/ "
    cmd += "-v /fastdata/ncov2019-arctic/SARS-CoV-2/V3:/ref/ " 
    cmd += "geoffw/picard1.67 "
    cmd += "java -jar /picard-tools-1.67/CollectInsertSizeMetrics.jar "
    cmd += "I=/in/"+bam+" "
    cmd += "R=/ref/nCoV-2019.reference.fasta "
    cmd += "H=/out/"+case+".hist "
    cmd += "O=/out/"+case+".txt"
    print("processing {}".format(case))
    subprocess.run(cmd, shell=True)


def parsePicard(bam_map):
    data = pd.DataFrame()
    for bamtuple in bam_map:
        case, bam, run_dir = bamtuple
        df=pd.read_csv(os.path.join(run_dir, case+".txt"), sep="\t", skiprows=6)
        r=df.loc[[0]]
        r['case']=case
        data=data.append(r, ignore_index=True)
    return data


def parseNextClade(fa_map):
    data = pd.DataFrame()
    for fatuple in fa_map:
        case, fa, run_dir = fatuple
        df=pd.read_json(os.path.join(run_dir, case+"_nextclade.json"))
        data=data.append(df, ignore_index=True)
    return data


def multithread(mymethod, poolsize, maplist):
    pool = Pool(poolsize)
    pool.map(mymethod, maplist)
    pool.close()
    pool.join()


if __name__ == "__main__":
    """
    Script to run generate extra QC information on COVID libraries:
    `Picard` and `nextclade` are  multithreaded and results parsed.
    an summary report is output with a row per sample.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--arctic", nargs=1, type=str, help="full path to artice pipeline output folder", required=True)
    parser.add_argument("-o", "--output", nargs=1, type=str, help="output csv filename including full path", required=True)
    args = parser.parse_args()
    bammap = getBamMap(args.arctic[0])
    famap = getFaMap(args.arctic[0])
    multithread(runPicard, 48, bammap)
    multithread(runNextClade, 48, bammap)
    picard = parsePicard(bammap, args.output[0])
    nextc = parseNextClade(famap, args.output[0])
    report.to_csv(args.output[0])