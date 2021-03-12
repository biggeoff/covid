# covid-extras

Area to store validation scripts and any extra code required for running the `ncov2019-artic-nf/` pipline

### To run the NF pipeline:

```bash
NXF_VER=20.10.0 nextflow run /home/geoffw/sandpit/ncov2019-artic-nf \
-profile conda \
--illumina \
--prefix "<outfile prefix>" \
--ivarBed /fastdata/ncov2019-arctic/nCoV-2019/V3/nCoV-2019.bed \
--alignerRefPrefix /fastdata/ncov2019-arctic/nCoV-2019/V3/nCoV-2019.reference.fasta \
--directory </path/to/illumina/run/bcl_files/> \
--outdir </path/to/illumina/run>/ncov2019-arctic-nf
```

### To get granular coverage information for Rob and the team run:

```bash
sudo python3 coverage.py -r /mnt/NGS_DATA_at_Bristol/COVID/untailed_runs_1_and_2/
```

### To verify lab work we need to check the fasta viral genomes match between the various lab conditions:
```
python3 ~/sandpit/covid-extras/compare_fasta.py
```
>currently hardcoded to compare tailed and untailed runs. (mnt/NGS_DATA_at_Bristol/COVID) will need argparse  to compare new data

### To classify lineages run Pangolin:
1. Launch the conda environment from the repo
2. Go to the artic output folder and concatenate all fastas
3. Run Pangolin

```bash
geoffw@nbsvr484:sandpit$ cd pangolin
geoffw@nbsvr484:pangolin$ conda activate pangolin
geoffw@nbsvr484:pangolin$cd /largedata/share/MiSeqOutput2/210212_M03605_0232_000000000-JH582/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus
geoffw@nbsvr484:ncovIllumina_sequenceAnalysis_makeConsensus$ cat *.fa > all_tailed_run1.fa
geoffw@nbsvr484:ncovIllumina_sequenceAnalysis_makeConsensus$ pangolin all_tailed_run1.fa
```

## Compare lineages against COG:
fasta comparison requires local copies of the fastas.
A quicker comparison checks out classifcation against the downloaded CLIMB metadata. This script also munges together the QC data to provide a much richer source of data for `validation`

```
geoffw@nbsvr484:covid-extras$ python compare_pangolin.py --help
usage: compare_pangolin.py [-h] -s SAMPLESHEET -c COG -p PANGOLIN -q QC -o
                           OUTPUT

optional arguments:
  -h, --help            show this help message and exit
  -s SAMPLESHEET, --samplesheet SAMPLESHEET
                        full path to SampleSheet (with lims and climb IDs)
  -c COG, --cog COG     full path to COG metadata download
  -p PANGOLIN, --pangolin PANGOLIN
                        full path to pangolin output
  -q QC, --qc QC        full path to qc output from pipeline
  -o OUTPUT, --output OUTPUT
                        full path to output results of the comparison to
```

### Convert the lineage output to ABI spec for upload to WinPath:


```bash
geoffw@nbsvr484:sandpit$ cd covid-extras
geoffw@nbsvr484:covid-extras$ python lineage2winpath.py
usage: lineage2winpath.py [-h] -l LINEAGE -o OUTPUT

optional arguments:
  -h, --help            show this help message and exit
  -l LINEAGE, --lineage LINEAGE
                        full path to artice pipeline output folder
  -o OUTPUT, --output OUTPUT
                        output csv filename including full path

geoffw@nbsvr484:covid-extras$ python lineage2winpath.py -l /largedata/share/MiSeqOutput2/210212_M03605_0232_000000000-JH582/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/lineage_report.csv -o /largedata/share/MiSeqOutput2/210212_M03605_0232_000000000-JH582/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/testy_test.txt
```

# Run Extras

To enrich QC information on cases a small supplementary pipeline has been made. This script leverages: `Picard` and `NextClade`:

```
geoffw@nbsvr484:covid-extras$ python run_extras.py --help
usage: run_extras.py [-h] -a ARCTIC -o OUTPUT

optional arguments:
  -h, --help            show this help message and exit
  -a ARCTIC, --arctic ARCTIC
                        full path to artice pipeline output folder
  -o OUTPUT, --output OUTPUT
                        output csv filename including full path
```