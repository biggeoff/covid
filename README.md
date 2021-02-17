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
