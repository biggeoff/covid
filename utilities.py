import os
import argparse
import subprocess
from glob import glob
import settings


def renameSubdir(arctic_dir, worklist, illumina):
    """ Replace worklist with illumina run name for upload to Majora """
    if os.path.exists(arctic_dir+'/qc_pass_climb_upload/'+worklist):
        print ("\nRenaming: qc_pass_climb_upload/{} to {}\n".format(worklist, illumina))
        os.rename(arctic_dir+'/qc_pass_climb_upload/'+worklist, 
            arctic_dir+'/qc_pass_climb_upload/'+illumina)


def getCLIMBsubdirs(arctic_dir, illumina):
    """ find the case folders under the CLIMB subdir """ 
    return glob(arctic_dir+'/qc_pass_climb_upload/'+illumina+'/*/')


def removeAfterDelim(subdirs, delim='_', count=1):
    """ remove the suffix after the case name """
    for sd in subdirs:
        bits = sd.split(delim)
        if len(bits) > count:
            new = delim.join(bits[:-count])
            os.rename(sd, new)
            print('renaming: {} -> {}'.format(sd, new))


def regorgArcticForUpload(arctic, worklist, run):
    """ Previously __main__ """
    renameSubdir(arctic, worklist, run)    
    subdirs = getCLIMBsubdirs(arctic, run)
    removeAfterDelim(subdirs, delim='-', count=1)


def copyToSampleNet(abi)
    """ Copy ABI formatted results into
    WinPath ingest area for automated
    upload to PHE/Pathology LIMS """
    shutil.copy(abi, settings.SAMPLENET)
    print ("Copied {} to Winpath: {}\n".format(abi, settings.SAMPLENET))


def copyToPHE(arctic_dir, worklist):
    """ Create a new directory under the worklist
    and copy run data to PHE area of the L drive """
    cmd="mkdir /mnt/cog-uk/Sequencing_Results/Local_Sequencing_Results/{}"
    subprocess.run(cmd, shell=True, executable='/bin/bash')
    cmd="rsync -azvP {}/ /mnt/cog-uk/Sequencing_Results/Local_Sequencing_Results/{}/".format(arctic_dir, worklist)
    subprocess.run(cmd, shell=True, executable='/bin/bash')


def copyToNGSDATA(arctic_dir, worklist):
    """ Copy to Genetics NGS analysis area """
    cmd="mkdir /mnt/NGS_DATA_at_Bristol/COVID/{}".format(arctic_dir, worklist)
    subprocess.run(cmd, shell=True, executable='/bin/bash')
    cmd="rsync -azvP {}/ /mnt/NGS_DATA_at_Bristol/COVID/{}".format(arctic_dir, worklist)
    subprocess.run(cmd, shell=True, executable='/bin/bash')


def scpCLIMB(arctic_dir, illumina):
    """ Upload to CLIMB servers in Birmingham """
    cmd = "scp -r {}/{} climb-covid19-woodwardg@bham.covid19.climb.ac.uk:upload/.".format(arctic_dir, illumina)
    subprocess.run(cmd, shell=True, executable='/bin/bash')
