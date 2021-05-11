import os
import argparse
from glob import glob


def renameSubdir(arctic_dir, worklist, illumina):
    if os.path.exists(arctic_dir+'/qc_pass_climb_upload/'+worklist):
        print ("\nRenaming: qc_pass_climb_upload/{} to {}\n".format(worklist, illumina))
        os.rename(arctic_dir+'/qc_pass_climb_upload/'+worklist, 
            arctic_dir+'/qc_pass_climb_upload/'+illumina)


def getCLIMBsubdirs(arctic_dir, illumina):
    return glob(arctic_dir+'/qc_pass_climb_upload/'+illumina+'/*/')


def removeAfterDelim(subdirs, delim='_', count=1):
    for sd in subdirs:
        bits = sd.split(delim)
        if len(bits) > count:
            new = delim.join(bits[:-count])
            os.rename(sd, new)
            print('renaming: {} -> {}'.format(sd, new))


if __name__ == "__main__":
    """
    removes all the extraneous info after the COG-UK ID in the sub dir names ready for CLIMB upload
    for example: 
        BEFORE:  .../ncov2019-arctic-nf/qc_pass_climb_upload/20210324/PHESW-YYBY8D-E11_S118_L001/
        AFTER:   .../ncov2019-arctic-nf/qc_pass_climb_upload/20210324/PHESW-YYBY8D

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--arctic", nargs=1, type=str, help="full path to arctic output folder", required=True)
    parser.add_argument("-w", "--worklist", nargs=1, type=str, help="Name of the worklist", required=True)
    parser.add_argument("-r", "--run", nargs=1, type=str, help="Name of the run", required=True)
    args = parser.parse_args()

    renameSubdir(args.arctic[0], args.worklist[0], args.run[0])    
    subdirs = getCLIMBsubdirs(args.arctic[0], args.run[0])
    removeAfterDelim(subdirs, delim='-', count=1)

