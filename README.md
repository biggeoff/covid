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
2. /mnt/cog-uk/Sequencing_Results/Local_Sequencing_Results/]
    > The entire run folder is deposited in the PHE area of Trust storage

The wrapper script automatically processes the output directories to prepare them for upload to CLIMB-UK and uses `scp` to upload the run to the following endpoint. This requires an account and `ssh` key. 
   * bham.covid19.climb.ac.uk/upload

### Running the wrapper

The wrapper script is executbale and uses the `usr/bin/python3.7` interpretter. To launch just type `covid` on the bash cli. It is recommended that you change directory into the run folder and use `${PWD}` to define the `-r/--run-dir` switch
```bash
covid –-help

optional arguments:
  -h, --help            show this help message and exit
  -d, --demux           Demultiplex BCLs to create fastq files
  -r RUN_DIR, --run_dir RUN_DIR
                        full path to Illumina run folder
  -w WORKLIST, --worklist WORKLIST
                        Name of the run/worklist
```

### To run Metadata upload to Majora:
```bash
soemthing
```