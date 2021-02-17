import os
import csv
import argparse
import subprocess
from multiprocessing.dummy import Pool


pool_size = 16
NF_ENV = 'NXF_VER=20.10.0'
arctic_dir = '/home/geoffw/sandpit/ncov2019-artic-nf'


def parseManifest(sspath):
    caselist = []
    body=False
    manifest = os.path.join(sspath, "SampleSheet.csv")
    with open(manifest, 'r') as ss:
        reader = csv.reader(ss, delimiter=',')
        for line in reader:
            if line[0] == "Sample_ID":
                body=True
                continue
            if body:
                caselist.append(os.path.join(sspath,'Data','Intensities','BaseCalls',line[7]))
    return caselist


def makeOutdir(case_dir):
    outdir = os.path.join(case_dir, "ncov2019-arctic-nf")
    if not os.path.isdir(outdir):
        print outdir
        #os.mkdir(outdir)
    return outdir


def launchArctic(case_dir):
    outdir = makeOutdir(case_dir)
    case = case_dir.split(os.sep)[-1]
    cmd = [NF_ENV, "nextflow", "run", arctic_dir,
    '-profile', 'conda', '--illumina', '--prefix', 
    '"'+case+'"', '--directory', case_dir, '--outdir', outdir]
    print "\n"+" ".join(cmd)
    #subprocess.run(cmd)


def multithread(mymethod, poolsize, maplist):
    pool = Pool(poolsize)
    pool.map(mymethod, maplist)
    pool.close()
    pool.join()


if __name__ == "__main__":
    """
    Pipeline for running COVID sequencing from MiSeq FastQ files.
    Requires that each case has been demultiplexed under it's own directory (Sample_Project)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--run", nargs=1, type=str, help="full path to MiSeq run folder directory (L drive)", required=True)
    args = parser.parse_args()

    case_map = parseManifest(args.run[0])
    #print case_map
    #for casedir in case_map:
    #    launchArctic(casedir)
    multithread(launchArctic, pool_size, case_map)
    