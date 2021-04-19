## OCARINA
import os
import subprocess
from glob import glob
import argparse
import time


def putLibrary(worklist, cog_id, std, err):
    cmd="ocarina put library "
    cmd+="--biosample "+cog_id+" VIRAL_RNA PCR AMPLICON 'ARTIC v3 (Tailed)' 'ARTIC v3' "
    cmd+="--library-layout-config PAIRED "
    cmd+="--library-name PHESW-LIB-"+worklist+" "
    cmd+="--library-seq-kit 'Illumina MiSeq v3' "
    cmd+="--library-seq-protocol 'MiSeq 300 Cycle'"
    std.write(cmd+"\n")
    std.flush()
    err.flush()
    proc = subprocess.Popen(cmd, shell=True, stdout=std, stderr=err)
    proc.wait()
    return 


def putSequencing(worklist, run, std, err, starttime='', endtime='', flowcell=''):
    cmd = "ocarina put sequencing "
    cmd+= "--instrument-make ILLUMINA "
    cmd+= "--instrument-model MiSeq "
    cmd+= "--library-name PHESW-LIB-"+worklist+" "
    cmd+= "--run-name "+run+" "
    cmd+= "--bioinfo-pipe-name 'ARTIC Pipeline (iVar)' "
    cmd+= "--bioinfo-pipe-version 1.3.0 " 
    cmd+= "--flowcell-type v3"
    std.write(cmd+"\n")
    std.flush()
    err.flush()
    proc = subprocess.Popen(cmd, shell=True, stdout=std, stderr=err)
    proc.wait()
    #result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    #std.write(result.stdout)
    #err.write(result.stderr)


def findCases(arctic_dir, subdir):
    """
    find all of the 
    """
    fullpaths = glob(arctic_dir+'/qc_pass_climb_upload/'+subdir+'/*/')
    cases = [f.strip('/').split("/")[-1] for f in fullpaths] # remove filepath
    parsed = [c for c in cases if not c.startswith("Pos")] # remove postive controls
    return cases


# get args
# find all cases in climb folder
# if mode == ocarina:
    # foreach sample put library
    # put sequencing
# if mode == csv:
    # foreach sample create line in csv 
    # output csv

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--arctic", nargs=1, type=str, help="full path to arctic output folder", required=True)
    parser.add_argument("-d", "--subdir", nargs=1, type=str, help="subdir to be uploaded to climb (miseq run)", required=True)
    parser.add_argument("-w", "--worklist", nargs=1, type=str, help="Name of the run/worklist", required=True)
    args = parser.parse_args()
    
    log = open(args.arctic[0]+'/ocarina.log', 'a')
    err = open(args.arctic[0]+'/ocarina.err', 'a')
    cases = findCases(args.arctic[0], args.subdir[0])
    for case in cases:
        putLibrary(args.worklist[0], case, log, err)
        time.sleep(2)
    
    putSequencing(args.worklist[0], args.subdir[0], log, err)
    log.close()
    err.close()

#### TESTING ####
#putLibrary('20210324', 'PHESW-YYBYRX')
##ocarina put library --biosample PHESW-YYBYRX VIRAL_RNA PCR AMPLICON 'ARTIC v3 (Tailed)' 'ARTIC v3' --library-layout-config PAIRED --library-name PHESW-LIB-20210324 --library-seq-kit 'Illumina MiSeq v3' --library-seq-protocol 'MiSeq 300 Cycle'
#putSequencing('20210324', '210401_M00132_0961_000000000-JLJKD')
##ocarina put sequencing --instrument-make ILLUMINA --instrument-model MiSeq --library-name PHESW-LIB-20210324 --run-name 210401_M00132_0961_000000000-JLJKD --bioinfo-pipe-name 'ARTIC Pipeline (iVar)' --bioinfo-pipe-version 1.3.0 --flowcell-type v3

#SUCCESS copying and pasting the commands into the shell !!!!!

#worklist='20210324'
#run= '210401_M00132_0961_000000000-JLJKD'
#arctic= '/largedata/share/MiSeqOutput/210401_M00132_0961_000000000-JLJKD/ncov2019-arctic-nf/'

#log = open(arctic+'/ocarina.log', 'a')
#err = open(arctic+'/ocarina.err', 'a')
#cases = findCases(arctic, worklist)
#for case in cases:
#    putLibrary(worklist, case, log, err)

#putSequencing(worklist, run, log, err)
#log.flush()
#err.flush()
#log.close()
#err.close()
# YESSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS done
#################