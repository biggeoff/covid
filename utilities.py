import os
import argparse
import subprocess
from glob import glob
import settings


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
        path = '/'.join(sd.strip('/').split('/')[:-1])
        bits = sd.strip('/').split('/')[-1]
        if len(bits) > 2: # PHESW-XXXXXXX
            new = os.path.join(path, delim.join(bits[0:1]))
            os.rename(sd, new)
            print('renaming: {} -> {}'.format(sd, new))


def regorgArcticForUpload(arctic, worklist, run):
    """ Previously __main__ """
    climb_dir = renameSubdir(arctic, worklist, run)    
    subdirs = getCLIMBsubdirs(climb_dir)
    removeAfterDelim(subdirs, delim='-', count=1)
    return climb_folder


def copyToSampleNet(abi):
    """ Copy ABI formatted results into
    WinPath ingest area for automated
    upload to PHE/Pathology LIMS """
    shutil.copy(abi, settings.SAMPLENET)
    print ("\nUploaded {} to Winpath LIMS: {}\n".format(abi, settings.SAMPLENET))


def copyToPHE(arctic_dir, worklist):
    """ Create a new directory under the worklist
    and copy run data to PHE area of the L drive """
    cmd="mkdir /mnt/cog-uk/Sequencing_Results/Local_Sequencing_Results/{}"
    subprocess.run(cmd, shell=True, executable='/bin/bash')
    cmd="rsync -azvP {}/ /mnt/cog-uk/Sequencing_Results/Local_Sequencing_Results/{}/".format(arctic_dir, worklist)
    subprocess.run(cmd, shell=True, executable='/bin/bash')
    print ("\nData copied to COG-UK area of L drive\n")


def copyToNGSDATA(arctic_dir, worklist):
    """ Copy to Genetics NGS analysis area """
    cmd="mkdir /mnt/NGS_DATA_at_Bristol/COVID/{}".format(arctic_dir, worklist)
    subprocess.run(cmd, shell=True, executable='/bin/bash')
    cmd="rsync -azvP {}/ /mnt/NGS_DATA_at_Bristol/COVID/{}".format(arctic_dir, worklist)
    subprocess.run(cmd, shell=True, executable='/bin/bash')
    print ("\n Run copied to NGS_DATA_at_Bristol\n")


def scpCLIMB(climb_dir):
    """ Upload to CLIMB servers in Birmingham """
    cmd = "scp -r {} climb-covid19-woodwardg@bham.covid19.climb.ac.uk:upload/.".format(climb_dir.strip('/'))
    subprocess.run(cmd, shell=True, executable='/bin/bash')
    print ("\n Run copied to CLIMB: bham.covid19.climb.ac.uk:upload \n")
