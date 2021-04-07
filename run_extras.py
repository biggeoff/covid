import os
import subprocess
from multiprocessing.dummy import Pool
import argparse
import pandas as pd


def getBamMap(run_dir):
    bams=[]
    files = os.listdir(os.path.join(run_dir, 'ncovIllumina_sequenceAnalysis_readMapping'))
    for bam in [f for f in files if f.endswith(".bam")]:
        case = "-".join(bam.split("-")[:-1])
        bams.append((case, bam, run_dir))
    return bams


def getFaMap(run_dir):
    fas=[]
    files = os.listdir(os.path.join(run_dir, 'ncovIllumina_sequenceAnalysis_makeConsensus'))
    for fa in [f for f in files if f.endswith(".fa")]:
        case = "-".join(fa.split("-")[:-1])
        fas.append((case, fa, run_dir))
    return fas


def runPangolin(run_dir, worklist):
    cmd = 'conda activate pangolin && '
    cmd += 'cat ncovIllumina_sequenceAnalysis_makeConsensus/*fa > '+worklist+'_all.fa && '
    cmd += 'pangolin '+worklist+'_all.fa --outfile '+worklist+'_lineage_report.csv && '
    cmd += 'conda deactivate'
    os.setuid(1005) # change to user: geoffw (not python for conda)
    subprocess.run(cmd, shell=True, executable='/bin/bash')
    list_dir = subprocess.Popen(["ls", "-l"])
    list_dir.wait()


def preexec_fn():
    os.setgid(1005)
    os.setuid(1005)


def prepareFastas(run_dir, worklist):
    fa_dir=os.path.join(run_dir, "ncovIllumina_sequenceAnalysis_makeConsensus")
    cmd['cat', os.path.join(fa_dir,'*fa'), '>', 
        os.path.join(fa_dir, worklist+'_all.fa')]
    subprocess.run(cmd, shell=True, executable='/bin/bash')


def runPangolinPOP(run_dir, worklist):
    """ NEED to set up PANGOLIN for ALL users 
    THIS DOES NOT WORK!!!! """
    fa=os.path.join(run_dir, "ncovIllumina_sequenceAnalysis_makeConsensus", worklist+'_all.fa')
    out=os.path.join(run_dir, worklist+'_lineage_report.csv')
    cmd = ['conda', 'run', '-n', 'pangolin', 
    'pangolin', fa, '--outfile', out]
    print (" ".join(cmd))
    #os.setuid(1005) # change to user: geoffw (not python for conda)
    pngo = subprocess.Popen(cmd, shell=True, executable='/bin/bash', 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=preexec_fn)
    stdout, stderr = pngo.communicate()
    print(stderr)


def runNextClade(row):
    case, fa, run_dir = row
    cmd = 'docker run --rm '
    cmd += '-v '+run_dir+'/ncovIllumina_sequenceAnalysis_makeConsensus/:/in/ '
    cmd += '-v '+run_dir+'/nextclade/:/out/ '
    cmd += 'nextstrain/nextclade nextclade '
    cmd += '-i /in/'+fa+' '
    cmd += '-o /out/'+case+'_nextclade.json '
    print("processing {}".format(case))
    subprocess.run(cmd, shell=True)


def runCovert(run_dir, worklist):
    config='/home/geoffw/sandpit/type_variants/arctic_config.csv'
    ref='/home/geoffw/sandpit/type_variants/MN908947.fa'
    out=os.path.join(run_dir, worklist+'_covert.csv')
    fa=os.path.join(run_dir, "ncovIllumina_sequenceAnalysis_makeConsensus", worklist+'.fa')
    cmd = ['python3', 'type_variants.py', '--append-genotypes',
        '--fasta-in', fa,
        '--variants-config', config,
        '--reference', ref,
        '--variants-out', out
    ]
    print("Running Covert over: {}".format(worklist+'.fa'))
    subprocess.run(cmd, shell=True)
    return out


def runPicard(row):
    case, bam, run_dir = row
    cmd= "docker run --rm "
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
        df=pd.read_csv(os.path.join(run_dir, 'picard', case+".txt"), sep="\t", skiprows=6)
        r=df.loc[[0]]
        r['case']=case
        data=data.append(r, ignore_index=True)
    return data


def parseNextCladeQC(fa_map):
    data = pd.DataFrame()
    for fatuple in fa_map:
        case, fa, run_dir = fatuple
        df=pd.read_json(os.path.join(run_dir, 'nextclade', case+"_nextclade.json"))
        try:
            qc = pd.json_normalize(df['qc'])
        except:
            qc = pd.DataFrame()
        r=df.loc[[0]] # subset full record to just 1 result
        qc['case']=r['seqName'].str.split('_').str[1].str.split('-').str[:-1].str.join('-')
        data=data.append(qc, ignore_index=True)
    return data


def parsePangolin(run_dir, worklist):
    df=pd.read_csv(os.path.join(run_dir, worklist+"_lineage_report.csv"))
    df['case']=df['taxon'].str.split("_").str[1].str.split("-").str[:-1].str.join('-')
    return df


def parseArcticQC(run_dir, worklist):
    df=pd.read_csv(os.path.join(run_dir, worklist+".qc.csv"))
    df['case']=df['sample_name'].str.split("_").str[0].str.split("-").str[:-1].str.join('-')
    return df


def parseCovert(covcsv):
    df = pd.read_csv(covcsv)
    df['case']=df['query'].str.split("_").str[0].str.split("-").str[:-1].str.join('-')
    return df


def multithread(mymethod, poolsize, maplist):
    pool = Pool(poolsize)
    pool.map(mymethod, maplist)
    pool.close()
    pool.join()


def makeReport(artic, picard, pang, nextc, covert, outdir, worklist):
    outfile=os.path.join(outdir, "{}_pic_pang_nextc_covert.qc.csv".format(worklist))
    report = pd.merge(left=artic, right=picard, left_on='case', right_on='case')
    report = pd.merge(left=report, right=pang, left_on='case', right_on='case')
    report = pd.merge(left=report, right=nextc, left_on='case', right_on='case')
    #report = pd.merge(left=report, right=covert, left_on='case', right_on='case')
    print("Report saved here:\n\t - {}".format(outfile))
    report.to_csv(outfile)
    return report


def makeTidyreport(df, outdir, worklist):
    #TODO
    outfile=os.path.join(outdir, "{}_report.csv".format(worklist))
    print("Report saved here:\n\t - {}".format(outfile))


if __name__ == "__main__":
    """
    Script to run generate extra QC information on COVID libraries:
    `Picard` and `nextclade` are  multithreaded and results parsed.
    an summary report is output with a row per sample.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--arctic", nargs=1, type=str, help="full path to artice pipeline output folder", required=True)
    parser.add_argument("-w", "--worklist", nargs=1, type=str, help="Name of the run/worklist", required=True)
    #parser.add_argument("-o", "--output", nargs=1, type=str, help="output csv filename including full path", required=True)
    args = parser.parse_args()
    bammap = getBamMap(args.arctic[0])
    #runPangolinPOP(args.arctic[0], args.worklist[0]) # CANT RUN CONDA FROM INSIDE SCRIPT 
    famap = getFaMap(args.arctic[0])
    multithread(runPicard, 48, bammap)
    for fa in famap:  # NextClade is already multithreaded
        runNextClade(fa)
    #covert_csv = runCovert(args.arctic[0], args.worklist[0])
    #covert = parseCovert(covert_csv)
    covert = ""
    picard = parsePicard(bammap)
    nextc = parseNextCladeQC(famap)
    arctic = parseArcticQC(args.arctic[0], args.worklist[0])
    pang = parsePangolin(args.arctic[0], args.worklist[0])

    data = makeReport(arctic, picard, pang, nextc, covert, args.arctic[0], args.worklist[0])
    #makeTidyReport(data, args.arctic[0], args.worklist[0])

