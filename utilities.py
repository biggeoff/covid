import os
import argparse
import subprocess
from glob import glob
import settings
from shutil import copy2


def renameSubdir(arctic_dir, worklist, illumina):
    """ Replace worklist with illumina run name for upload to Majora """
    src=arctic_dir+'/qc_pass_climb_upload/'+worklist
    dest=arctic_dir+'/qc_pass_climb_upload/'+illumina
    if os.path.exists(arctic_dir+'/qc_pass_climb_upload/'+worklist):
        print ("\nRenaming: qc_pass_climb_upload/{} to {}\n".format(worklist, illumina))
        os.rename(src, dest)
    return dest


def getCLIMBsubdirs(climb_dir):
    """ find the case folders under the CLIMB subdir """ 
    return glob(climb_dir+'/*/')


def removeAfterDelim(subdirs, delim='_'):
    """ remove the suffix after the case name """
    for sd in subdirs:
        path = '/'.join(sd.rstrip('/').split('/')[:-1])
        bits = sd.rstrip('/').split('/')[-1].split(delim)
        if len(bits) > 2: # PHESW-XXXXXXX
            new = os.path.join(path, delim.join(bits[0:1]))
            os.rename(sd, new)
            print('renaming: {} -> {}'.format(sd, new))


def reorganiseForCLIMB(arctic, worklist, run):
    """ Previously __main__ """
    climb_dir = renameSubdir(arctic, worklist, run)    
    subdirs = getCLIMBsubdirs(climb_dir)
    removeAfterDelim(subdirs, delim='-')
    return climb_dir


def copyToSampleNet(abi):
    """ Copy ABI formatted results into
    WinPath ingest area for automated
    upload to PHE/Pathology LIMS """
    copy2(abi, settings.SAMPLENET)
    print ("\nUploaded {} to Winpath LIMS: {}\n".format(abi, settings.SAMPLENET))


def copyToPHE(arctic_dir, worklist):
    """ Create a new directory under the worklist
    and copy run data to PHE area of the L drive """
    dest="/mnt/cog-uk/Sequencing_Results/Local_Sequencing_Results/{}".format(worklist)
    if not os.path.exists(dest):
        os.mkdir(dest)
    print ("\nCopying Data to COG-UK area of L drive.....\n")
    cmd="rsync -azvP {}/ {}/".format(arctic_dir, dest)
    subprocess.run(cmd, shell=True, executable='/bin/bash')


def copyToNGSDATA(arctic_dir, worklist):
    """ Copy to Genetics NGS analysis area """
    dest="/mnt/NGS_DATA_at_Bristol/COVID/{}".format(worklist)
    if not os.path.exists(dest):
        os.mkdir(dest)
    print ("\n Copying data to NGS_DATA_at_Bristol...\n")
    cmd="rsync -azvP {}/ {}/".format(arctic_dir, dest)
    subprocess.run(cmd, shell=True, executable='/bin/bash')


def scpCLIMB(climb_dir):
    """ Upload to CLIMB servers in Birmingham """
    cmd = "scp -r {} {}@{}:upload/.".format(climb_dir.rstrip('/'),
        settings.CLIMB_USER, settings.CLIMB_URL)
    subprocess.run(cmd, shell=True, executable='/bin/bash')
    print ("\n Run copied to CLIMB: bham.covid19.climb.ac.uk:upload \n")
