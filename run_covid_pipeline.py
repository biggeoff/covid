#!/usr/bin/python3

import os
import subprocess
from multiprocessing.dummy import Pool
import argparse
import pandas as pd
import settings
import utilities
import winpath


def RunBCL2fastq(run_dir):
	"""Create cmd string and execute BCL2fastq2 in Docker """
	mnts="-v {}:/run".format(run_dir) 
	out_dir="/run/Data/Intensities/BaseCalls/"

	cmd="docker run "+mnts+" "+settings.BCL2FASTQ2_CONTAINER+" "+settings.BCL2FASTQ_EXE
	cmd+=" -R /run -o "+out_dir+" --barcode-mismatches 0 --ignore-missing-bcls "
	cmd+="--ignore-missing-filter --ignore-missing-positions --sample-sheet /run/SampleSheet.csv"
	subprocess.call([ cmd ], shell=True)


def loadSS(rundir):
    """ read and return the samplesheet into a pandas dataframe"""
    ss = os.path.join(rundir, 'SampleSheet.csv')
    df=pd.read_csv(ss, skiprows=19)
    return df


def getBamMap(run_dir):
    """ return a map of BAMs for multiprocessing """
    bams=[]
    files = os.listdir(os.path.join(run_dir, 'ncovIllumina_sequenceAnalysis_readMapping'))
    for bam in [f for f in files if f.endswith(".bam")]:
        case = "-".join(bam.split("-")[:-1])
        bams.append((case, bam, run_dir))
    return bams


def getFaMap(run_dir):
    """ return a map of FASTAs for multiprocessing """
    fas=[]
    files = os.listdir(os.path.join(run_dir, 'ncovIllumina_sequenceAnalysis_makeConsensus'))
    for fa in [f for f in files if f.endswith(".fa")]:
        case = "-".join(fa.split("-")[:-1])
        fas.append((case, fa, run_dir))
    return fas


def getVCFMap(run_dir):
    """ return a map of VCFs for multiprocessing """
    vcfs=[]
    files = os.listdir(os.path.join(run_dir, 'ncovIllumina_sequenceAnalysis_callVariants'))
    for vcf in [f for f in files if f.endswith(".tsv")]:
        case = "-".join(vcf.split("-")[:-1])
        vcfs.append((case, vcf, run_dir))
    return vcfs


def runArctic(run_dir, worklist):
    """ run the Arctic NF pipeline """
    ref = settings.ARCTIC_RESOURCE + settings.ARCTIC_REF
    arctic_out = os.path.join(run_dir, 'ncov2019-arctic-nf')
    cmd = "NXF_VER=20.10.0 NXF_WORK=/tmp "
    cmd += "nextflow run "+settings.ARCTIC_PATH+" "
    cmd += "-profile conda "
    cmd += "--cache "+settings.ARCTIC_CACHE+" "
    cmd += "--illumina "
    cmd += "--prefix "+worklist+" "
    cmd += "--ivarBed "+settings.ARCTIC_BED+" "
    cmd += "--alignerRefPrefix "+ref+" "
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
    """ Combine all Fastas into single file 
    output into run_dir using BASH shell """
    cmd = 'cat '+ os.path.join(run_dir, 'ncovIllumina_sequenceAnalysis_makeConsensus', '*fa')
    cmd += ' > '+  os.path.join(run_dir, worklist+'.fa')
    print (cmd)
    subprocess.run(cmd, shell=True, executable='/bin/bash')


def runPangolinDocker(run_dir, worklist):
    """ 
    check for updates and run Pangolin
    using Docker 
    Creates <worklist>_lineage_report.csv
    """
    cmd = 'docker run -v '+run_dir+'/:/test/ --rm '
    cmd += settings.PANGOLIN_DOCKER+' bash -c "' 
    cmd += 'pangolin --update && pangolin /test/'+worklist+'.fa '
    cmd += '--outfile /test/'+worklist+'_lineage_report.csv"'
    print (cmd)
    subprocess.run(cmd, shell=True, executable='/bin/bash')


def runNextClade(row):
    case, fa, run_dir = row
    cmd = 'docker run --rm '
    cmd += '-v '+run_dir+'/ncovIllumina_sequenceAnalysis_makeConsensus/:/in/ '
    cmd += '-v '+run_dir+'/nextclade/:/out/ '
    cmd += settings.NEXTCLADE_DOCKER+' nextclade '
    cmd += '-i /in/'+fa+' '
    cmd += '-o /out/'+case+'_nextclade.json '
    print("processing {}".format(case))
    subprocess.run(cmd, shell=True)


def runPicard(row):
    case, bam, run_dir = row
    cmd= "docker run --rm "
    cmd += "-v "+run_dir+"/ncovIllumina_sequenceAnalysis_readMapping/:/in/ "
    cmd += "-v "+run_dir+"/picard/:/out/ "
    cmd += "-v "+settings.ARCTIC_RESOURCE+":/ref/ " 
    cmd += settings.PICARD_DOCKER+" "
    cmd += "java -jar "+settings.PICARD_JAR+" "
    cmd += "I=/in/"+bam+" "
    cmd += "R=/ref/"+settings.ARCTIC_REF+" "
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
    print(os.path.join(run_dir, worklist+"_lineage_report.csv"))
    df=pd.read_csv(os.path.join(run_dir, worklist+"_lineage_report.csv"))
    df['case']=df['taxon'].str.split("_").str[1].str.split("-").str[:-1].str.join('-')
    print(df)
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


def printFinalMessage():
    message = """============================================================
    \n BGL / PHESW COVID Wrapper Script has completed....
    \n============================================================
    \n... don't forget to download a new token from Majora:
    \n\t*\thttps://majora.covid19.climb.ac.uk/keys/list/
    \n1. Save the token here: ~/ocarina
    \n2. Run the upload: ocarina_API.py \n{}""".format(settings.OCARINA)
    print(message)



if __name__ == "__main__":
    """
    Script to run Arctic pipeline & generate extra QC information on COVID libraries:
    `Picard` and `nextclade` are  multithreaded and results parsed.
    Two reports are output with a row per sample.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--demux", help="Demultiplex BCLs to create fastq files", action="store_true", required=False)
    parser.add_argument("-r", "--run_dir", nargs=1, type=str, help="full path to Illumina run folder", required=True)
    parser.add_argument("-w", "--worklist", nargs=1, type=str, help="Name of the run/worklist", required=True)
    args = parser.parse_args()
    run = args.run_dir[0]
    illumina = run.strip('/').split('/')[-1]
    wl = args.worklist[0]
    arctic_dir = run+"/ncov2019-arctic-nf/"

    # Run Pipeline
    ss = loadSS(run)
    if args.demux:
        RunBCL2fastq(run)
    
    arctic_dir = runArctic(run, wl)
    arctic_dir=run+"/ncov2019-arctic-nf"
    
    # Run extra annotation and QC
    createRunFasta(arctic_dir, wl)
    runPangolinDocker(arctic_dir, wl)
    bammap = getBamMap(arctic_dir)
    famap = getFaMap(arctic_dir)
    vcfmap = getVCFMap(arctic_dir)
    multithread(runPicard, 48, bammap)
    for fa in famap:  # NextClade is already multithreaded
        runNextClade(fa)
    
    # Parse in all datasets
    picard = parsePicard(bammap)
    nextc = parseNextCladeQC(famap)
    arctic = parseArcticQC(arctic_dir, wl)
    pang = parsePangolin(arctic_dir, wl)
    E484K = parseVCFsForLocus(vcfmap, 23012, "E484K", 'A')
    
    # output final reports
    abi_file = winpath.lineage2ABI(ss, arctic_dir, wl)
    data = makeReport(ss, arctic, picard, pang, nextc, E484K, arctic_dir, wl)
    makeLocalReport(data, arctic_dir, wl)

    # Copy data to all network locations
    #utilities.regorgArcticForUpload(arctic_dir, wl, illumina)
    # copy to sample net
    #utilities.copyToSamplenet(abi_file)
    # copy to COG-UK
    #utilities.copyToPHE(arctic_dir, worklist)
    # COPY to L -- can't do this without sudo (need to remount)
    #utilities.copyToNGSDATA(arctic_dir, worklist)
    # Secure cOPY the data to the CLIMB servers in Birmingham
    #utilities.scpCLIMB(arctic_dir, illumina)
    # Print reminder to UPLOAD to Majora
    #printFinalMessage()



