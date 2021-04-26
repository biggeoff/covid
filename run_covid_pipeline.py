import os
import subprocess
from multiprocessing.dummy import Pool
import argparse
import pandas as pd


def loadSS(rundir):
    ss = os.path.join(rundir, 'SampleSheet.csv')
    df=pd.read_csv(ss, skiprows=19)
    return df


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


def runArctic(run_dir, worklist):
    """ run the NF pipeline """
    arctic_out = os.path.join(run_dir, 'ncov2019-arctic-nf')
    cmd = "NXF_VER=20.10.0 NXF_WORK=/tmp "
    cmd += "nextflow run /home/geoffw/sandpit/ncov2019-artic-nf "
    cmd += "-profile conda "
    cmd += "--cache /home/geoffw/miniconda3/envs/artic-ncov2019-illumina/ "
    cmd += "--illumina "
    cmd += "--prefix "+worklist+" "
    cmd += "--ivarBed /fastdata/ncov2019-arctic/nCoV-2019/V3/nCoV-2019.bed "
    cmd += "--alignerRefPrefix /fastdata/ncov2019-arctic/nCoV-2019/V3/nCoV-2019.reference.fasta "
    cmd += "--directory " + run_dir + " "
    cmd += "--outdir " + arctic_out
    print ("\n Runninng Artic v4 Pipeline....\n")
    print (cmd+"\n")
    std = open(os.path.join(run_dir, 'arctic.log'), 'a')
    err = open(os.path.join(run_dir, 'arctic.err'), 'a')
    proc = subprocess.Popen(cmd, shell=True, stdout=std, stderr=err)
    proc.wait()
    return arctic_out


def createRunFasta(run_dir, worklist):
    cmd = 'cat '+ os.path.join(run_dir, 'ncovIllumina_sequenceAnalysis_makeConsensus/*fa')
    cmd += ' > '+  os.path.join(run_dir, worklist+'.fa')
    print (cmd)
    subprocess.run(cmd, shell=True, executable='/bin/bash')


def runPangolinDocker(run_dir, worklist):
    cmd = ['docker', 'run', '-v', run_dir+'/:/test/', '--rm',
        'staphb/pangolin', 'pangolin', '/test/'+worklist+'.fa',
        '--outfile', '/test/'+worklist+'_lineage_report.csv']
    cmd_str = ' '.join(cmd) 
    print (cmd_str)
    subprocess.run(cmd_str, shell=True, executable='/bin/bash')


def prepareFastas(run_dir, worklist):
    fa_dir=os.path.join(run_dir, "ncovIllumina_sequenceAnalysis_makeConsensus")
    cmd['cat', os.path.join(fa_dir,'*fa'), '>', 
        os.path.join(fa_dir, worklist+'_all.fa')]
    subprocess.run(cmd, shell=True, executable='/bin/bash')


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


def parseVCFsForLocus(vcfmap, locus, locus_name, allele):
    matches=pd.DataFrame()
    for case, vcf, path in vcfmap:
        data = pd.read_csv(os.path.join(path, 'ncovIllumina_sequenceAnalysis_callVariants', vcf), sep="\t", header=0)
        if data[(data.POS == locus) & (data.ALT == allele)].shape[0] > 0:
            hits = data[(data.POS == locus) & (data.ALT == allele)]
            hits['case'] = case
            matches = matches.append(hits)
    if matches.shape[0] > 0:
        matches = matches.reindex(columns=['case','ALT_FREQ', 'PASS'])
        matches = matches.rename(columns={'ALT_FREQ':locus_name, 'PASS':locus_name+'_PASS'})
    return matches



def multithread(mymethod, poolsize, maplist):
    pool = Pool(poolsize)
    pool.map(mymethod, maplist)
    pool.close()
    pool.join()


def makeReport(ss, artic, picard, pang, nextc, E484K, outdir, worklist):
    outfile=os.path.join(outdir, "{}_full_report.csv".format(worklist))
    report = pd.merge(left=ss, right=arctic, left_on='Sample_ID', right_on='case')
    report = pd.merge(left=report, right=picard, left_on='case', right_on='case')
    report = pd.merge(left=report, right=pang, left_on='case', right_on='case')
    report = pd.merge(left=report, right=nextc, left_on='case', right_on='case')
    report = pd.merge(left=report, right=E484K, left_on='case', right_on='case', how='left')
    print("Report saved here:\n\t - {}".format(outfile))
    report.to_csv(outfile)
    return report


def makeLocalReport(df, outdir, worklist):
    outfile=os.path.join(outdir, "{}_lineage_E484K.csv".format(worklist))
    report = df.reindex(columns=['Column1','Sample_ID', 'lineage', 'E484K', 'status', 'note',  'E484K_PASS'])
    header=['Lab Number','COG-UKID','Lineage', 'E484K', 'Pango QC', 'Pango note', 'E484K_QC']
    report.columns=header
    report.to_csv(outfile)
    print("Report saved here:\n\t - {}".format(outfile))


if __name__ == "__main__":
    """
    Script to run Arctic pipeline & generate extra QC information on COVID libraries:
    `Picard` and `nextclade` are  multithreaded and results parsed.
    Two reports are output with a row per sample.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--run_dir", nargs=1, type=str, help="full path to Illumina run folder", required=True)
    parser.add_argument("-w", "--worklist", nargs=1, type=str, help="Name of the run/worklist", required=True)
    args = parser.parse_args()
    ss = loadSS(args.run_dir[0])
    # Run Pipeline
    arctic_dir = runArctic(args.run_dir[0], args.worklist[0])
    # Run extra annotation and QC
    createRunFasta(arctic_dir, args.worklist[0])
    runPangolinDocker(arctic_dir, args.worklist[0])
    bammap = getBamMap(arctic_dir)
    famap = getFaMap(arctic_dir)
    multithread(runPicard, 48, bammap)
    for fa in famap:  # NextClade is already multithreaded
        runNextClade(fa)
    # Parse in all datasets
    picard = parsePicard(bammap)
    nextc = parseNextCladeQC(famap)
    arctic = parseArcticQC(arctic_dir, args.worklist[0])
    pang = parsePangolin(arctic_dir, args.worklist[0])
    E484K = parseVCFsForLocus(vcfmap, 23012, "E484K", 'A')
    # output final reports
    data = makeReport(ss, arctic, picard, pang, nextc, E484K, arctic_dir, args.worklist[0])
    makeLocalReport(data, arctic_dir, args.worklist[0])

