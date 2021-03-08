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


def runPicard(row):
    case, bam, run_dir = row
    cmd= "sudo docker run --rm "
    cmd += "-v "+run_dir+":/run/ "
    cmd += "-v /fastdata/ncov2019-arctic/SARS-CoV-2/V3:/ref/ " 
    cmd += "geoffw/picard1.67 "
    cmd += "java -jar /picard-tools-1.67/CollectInsertSizeMetrics.jar "
    cmd += "I=/run/"+bam+" "
    cmd += "R=/ref/nCoV-2019.reference.fasta "
    cmd += "H=/run/"+case+".hist "
    cmd += "O=/run/"+case+".txt"
    print("processing {}".format(case))
    subprocess.run(cmd, shell=True)


def makeReport(bam_map, report):
    data = pd.DataFrame()
    for bamtuple in bam_map:
        case, bam, run_dir = bamtuple
        df=pd.read_csv(os.path.join(run_dir, case+".txt"), sep="\t", skiprows=6)
        r=df.loc[[0]]
        r['case']=case
        data=data.append(r, ignore_index=True)
    return data



def multithread(mymethod, poolsize, maplist):
    pool = Pool(poolsize)
    pool.map(mymethod, maplist)
    pool.close()
    pool.join()


if __name__ == "__main__":
    """
    Script to run picard and parse out insert size
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--alignment", nargs=1, type=str, help="full path to artice pipeline BAM output folder", required=True)
    parser.add_argument("-o", "--output", nargs=1, type=str, help="output csv filename including full path", required=True)
    args = parser.parse_args()
    bammap = getBamMap(args.alignment[0])
    #multithread(runPicard, 48, bammap)
    report = makeReport(bammap, args.output[0])
    report.to_csv(args.output[0])