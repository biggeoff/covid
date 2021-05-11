# COVID v1.0.1
### Author: Geoff Woodward [11/05/2021]
## Automated Arctic Pipeline Wrapper Script

This wrapper script runs the Arctic v3 COVID pipeline and supplements with further tools:
1. Pangolin (assigns COVID lineage - in line with national CLIMB system)
2. Picard (insert size metrics)
2. NextClade (further QC and lineage data)

All data is then parsed to create three output reports:
1. Lineage and E484K status for scientists and reporting (txt)
2. Full report of all tools and QC (txt)
3. Lineage ABI file for upload to WinPath LIMS

Pipeline data is sent to endpoints locally:
1. /mnt/PHEfftransfer/ABI7500_1/ 
    > ABI file is deposited here for upload to WinPath LIMS
2. /mnt/cog-uk/Sequencing_Results/Local_Sequencing_Results/
    > The entire run folder is deposited in the PHE area of Trust storage

The wrapper script automatically processes the output directories to prepare them for upload to CLIMB-UK and uses `scp` to upload the run to the following endpoint. This requires an account and `ssh` key. 
   * bham.covid19.climb.ac.uk/upload

### Running the wrapper

The wrapper script is executable and uses the `usr/bin/python3.7` interpreter. To launch just type `covid` on the bash cli. It is recommended that you change directory into the run folder and use `${PWD}` to define the `-r/--run-dir` switch. If the run hasn't been demultiplexed make sure to use the `-d/--demux` switch. Finally supply the worklist with the `-w/--worklist` switch, for example: `-w 20210430.1-20210505.1`
```bash
$ covid –-help

optional arguments:
  -h, --help            show this help message and exit
  -d, --demux           Demultiplex BCLs to create fastq files
  -r RUN_DIR, --run_dir RUN_DIR
                        full path to Illumina run folder
  -w WORKLIST, --worklist WORKLIST
                        Name of the run/worklist

$ covid -r ${PWD} -w 20210430.1-20210505.1
```

### Updating Metadata on Majora:

Again this script is executable and uses the `usr/bin/python3.7` interpreter. To launch just type `updatemaj` on the bash cli. It is recommended that you change directory into the run folder and use `${PWD}/ncov2019-arctic-nf ` to define the `-a/--arctic` switch. Sse the `-d/--subdir` switch to define the run name on Majora, for example `-d 210507_M03605_0262_000000000-JMF5P` . Finally supply the worklist with the `-w/--worklist` switch, for example: `-w 20210430.1-20210505.1`
```bash
$ updatemaj --help
usage: ocarina_API.py [-h] -a ARCTIC -d SUBDIR -w WORKLIST

optional arguments:
  -h, --help            show this help message and exit
  -a ARCTIC, --arctic ARCTIC
                        full path to arctic output folder
  -d SUBDIR, --subdir SUBDIR
                        subdir to be uploaded to climb (miseq run)
  -w WORKLIST, --worklist WORKLIST
                        Name of the run/worklist

$ updatemaj -a ${PWD}/ncov2019-arctic-nf -d 210507_M03605_0262_000000000-JMF5P -w 20210430.1-20210505.1 
```

> Please refer to QPulse SOP 25.9 for the full operating instructions and information surrounding this pipeline.

