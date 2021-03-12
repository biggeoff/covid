# Testing the Arctic NF Pipeline

## Downloading FastQs from Ensemble

``` 
wget link  = can't acess the FTP site so had to download manually!!! boooo
wget link
wget link
wget link
```
https://www.ebi.ac.uk/ena/browser/view/SAMEA7611438

> some useful info

## Run the pipeline

When running DO NOT USE sudo -  ** sudo can not run conda**

We have an old version of nextflow:
```bash
geoffw@nbsvr484:~/sandpit/ncov2019-artic-nf$ nextflow -version
/usr/local/bin/nextflow: line 458: /home/geoffw/.nextflow/tmp/launcher/nextflow-one_19.07.0/nbsvr484/classpath-f274f269f5b8a04c90822ca761e1f633: Permission denied

      N E X T F L O W
      version 19.07.0 build 5106
      created 27-07-2019 13:22 UTC (14:22 BST)
      cite doi:10.1038/nbt.3820
      http://nextflow.io
```

However Nextflow is amazing and this can be easily be overcome without having to upgrade and risk potential issues with existing pipelines.

Just set an environment variable before the nextflow command and it will automatically download and use the stated version:

```bash
NXF_VER=20.10.0 nextflow run ....
```

First test that passed correctly was run like this:

```bash
geoffw@nbsvr484:~/sandpit/ncov2019-artic-nf$ NXF_VER=20.10.0 nextflow run . -profile conda --illumina --prefix "test" --directory /RUN_FOLDERS/NextSeqOutput/210203_COVID_ENA/ERR4868520/
N E X T F L O W  ~  version 20.10.0
Launching `./main.nf` [backstabbing_archimedes] - revision: cf9fb463d5
WARN: DSL 2 IS AN EXPERIMENTAL FEATURE UNDER DEVELOPMENT -- SYNTAX MAY CHANGE IN FUTURE RELEASE
executor >  local (7)
executor >  local (10)
[db/78622e] process > ncovIllumina:prepareReferenceFiles:articDownloadScheme (https://github.com/artic-network/... [100%] 1 of 1 ✔
[03/67c410] process > ncovIllumina:prepareReferenceFiles:indexReference (nCoV-2019.reference.fasta)                [100%] 1 of 1 ✔
[fc/e46fd4] process > ncovIllumina:sequenceAnalysis:readTrimming (ERR4868520)                                      [100%] 1 of 1 ✔
[ad/e75af3] process > ncovIllumina:sequenceAnalysis:readMapping (ERR4868520)                                       [100%] 1 of 1 ✔
[ad/45604f] process > ncovIllumina:sequenceAnalysis:trimPrimerSequences (ERR4868520)                               [100%] 1 of 1 ✔
[72/13f0eb] process > ncovIllumina:sequenceAnalysis:callVariants (ERR4868520)                                      [100%] 1 of 1 ✔
[ce/e245a3] process > ncovIllumina:sequenceAnalysis:makeConsensus (ERR4868520)                                     [100%] 1 of 1 ✔
[7e/943b27] process > ncovIllumina:sequenceAnalysis:makeQCCSV (ERR4868520)                                         [100%] 1 of 1 ✔
[87/70a7d2] process > ncovIllumina:sequenceAnalysis:writeQCSummaryCSV (test)                                       [100%] 1 of 1 ✔
[0e/61a022] process > ncovIllumina:sequenceAnalysis:collateSamples (ERR4868520)                                    [100%] 1 of 1 ✔            Completed at: 04-Feb-2021 15:59:41
Duration    : 10m 13s
CPU hours   : 0.2
Succeeded   : 10
```

Performance slow when single sample.
test running over all downloads from ENA (removed several as fastqs weren't valid)
pinch points:

1. Download & index of reference 
2. Conda environment setup

fasta and bed files copied to /fastdata/

Much more efficient running over entire run directory - only runs single sample through each process - so more optimisation could be done:

```
geoffw@nbsvr484:~$ NXF_VER=20.10.0 nextflow run /home/geoffw/sandpit/ncov2019-artic-nf -profile conda --illumina --prefix "210203_COVID_ENA" --ivarBed /fastdata/ncov2019-arctic/nCoV-2019/V3/nCoV-2019.bed --alignerRefPrefix /fastdata/ncov2019-arctic/nCoV-2019/V3/nCoV-2019.reference.fasta --directory 210203_COVID_ENA/Data/Intensities/BaseCalls/ --outdir 210203_COVID_ENA/ncov2019-arctic-nf
N E X T F L O W  ~  version 20.10.0
Launching `/home/geoffw/sandpit/ncov2019-artic-nf/main.nf` [prickly_mcclintock] - revision: cf9fb463d5
WARN: DSL 2 IS AN EXPERIMENTAL FEATURE UNDER DEVELOPMENT -- SYNTAX MAY CHANGE IN FUTURE RELEASE
executor >  local (59)
executor >  local (60)
executor >  local (60)
executor >  local (87)
[3a/8569c0] process > ncovIllumina:prepareReferenceFiles:articDownloadScheme (https:/... [100%] 1 of 1 ✔
[57/22b126] process > ncovIllumina:prepareReferenceFiles:indexReference (nCoV-2019.re... [100%] 1 of 1 ✔
[d7/26a784] process > ncovIllumina:sequenceAnalysis:readTrimming (ERR4868721)            [100%] 12 of 12 ✔
[21/b4dcbb] process > ncovIllumina:sequenceAnalysis:readMapping (ERR4868721)             [100%] 12 of 12 ✔
[e2/13e21b] process > ncovIllumina:sequenceAnalysis:trimPrimerSequences (ERR4869689)     [100%] 12 of 12 ✔
[cd/9dbba3] process > ncovIllumina:sequenceAnalysis:callVariants (ERR4869689)            [100%] 12 of 12 ✔
[44/1ecc46] process > ncovIllumina:sequenceAnalysis:makeConsensus (ERR4869689)           [100%] 12 of 12 ✔
[ae/bbf864] process > ncovIllumina:sequenceAnalysis:makeQCCSV (ERR4869689)               [100%] 12 of 12 ✔
[d4/eb1d4a] process > ncovIllumina:sequenceAnalysis:writeQCSummaryCSV (210203_COVID_ENA) [100%] 1 of 1 ✔
[89/7a9415] process > ncovIllumina:sequenceAnalysis:collateSamples (ERR4869689)          [100%] 12 of 12 ✔
Completed at: 09-Feb-2021 16:51:45
Duration    : 18m 2s
CPU hours   : 3.1
Succeeded   : 87

```
Copied to the L drive and emailed to team.
```
cd /home/geoffw/210203_COVID_ENA/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/
cat * > pipeline_test_consensus.fa
sudo cp pipeline_test_consensus.fa /RUN_FOLDERS/MiSeqOutput/210203_COVID_ENA/
```

# Tested access to CLIMB:
```
geoffw@nbsvr484:~/$ cat test_upload.txt 
testing connection from NBT NHS Trust - Geoff Woodward Bioinformatics from server NBSVR484 [10.229.248.19]
Proposed pathway for uploading Arctic COVID sequencing data from MiSeq platform
geoffw@nbsvr484:~/$ scp test_upload.txt climb-covid19-woodwardg@bham.covid19.climb.ac.uk:upload
test_upload.txt                                        100%  187   18.3KB/s    00:00
```

# Temperature Optimisation
Process the validation run to compare temperatures:

```
geoffw@nbsvr484:~$ cd /largedata/share/MiSeqOutput/
geoffw@nbsvr484:/largedata/share/MiSeqOutput/$ sudo chown -R geoffw:geoffw 210206_M00132_0944_000000000-JH7CB
geoffw@nbsvr484:/largedata/share/MiSeqOutput/$ cd 210206_M00132_0944_000000000-JH7CB
geoffw@nbsvr484:/largedata/share/MiSeqOutput/210206_M00132_0944_000000000-JH7CB$ NXF_VER=20.10.0 nextflow run /home/geoffw/sandpit/ncov2019-artic-nf -profile conda --illumina --prefix "untailedRun1and2" --ivarBed /fastdata/ncov2019-arctic/nCoV-2019/V3/nCoV-2019.bed --alignerRefPrefix /fastdata/ncov2019-arctic/nCoV-2019/V3/nCoV-2019.reference.fasta --directory /largedata/share/MiSeqOutput/210206_M00132_0944_000000000-JH7CB/Data/Intensities/BaseCalls/ --outdir /largedata/share/MiSeqOutput/210206_M00132_0944_000000000-JH7CB/ncov2019-arctic-nf
```


Process second run

```
NXF_VER=20.10.0 nextflow run /home/geoffw/sandpit/ncov2019-artic-nf -profile conda --illumina --prefix "tailedRun1" --ivarBed /fastdata/ncov2019-arctic/nCoV-2019/V3/nCoV-2019.bed --alignerRefPrefix /fastdata/ncov2019-arctic/nCoV-2019/V3/nCoV-2019.reference.fasta --directory /largedata/share/MiSeqOutput2/210212_M03605_0232_000000000-JH582/Data/Intensities/BaseCalls/ --outdir /largedata/share/MiSeqOutput2/210212_M03605_0232_000000000-JH582/ncov2019-arctic-nf
```

indexes wrong:

copy over bcl files:

```
geoffw@nbsvr484:/largedata/share/MiSeqOutput2/210212_M03605_0232_000000000-JH582$ rsync -azvP --include "*/" --include "*xml" \--include "*csv" --include "*txt" --include "*bin" --include "*bcl" --include **"*bci"** --exclude "*" /RUN_FOLDERS//MiSeqOutput2/210212_M03605_0232_000000000-JH582 /largedata/share/MiSeqOutput2/
```

demux:

```
docker run -v /largedata/share/MiSeqOutput2/
210212_M03605_0232_000000000-JH582/:/run/ \
geoffw/centos_bcl2fastq2 \
bcl2fastq -R /run -o /run/Data/Intensities/BaseCalls \
--barcode-mismatches 0 --ignore-missing-bcls \
--ignore-missing-filter --ignore-missing-positions \
--sample-sheet /run/SampleSheet.csv
```

# Compare fasta sequences:

### Install BioPython...
```bash
sudo -H pip3 install biopython
cd /mnt/NGS_DATA_at_Bristol/COVID$
```

Now test comparing fasta sequences... with the new script compare_fasta.py
```bash
cd /mnt/NGS_DATA_at_Bristol/COVID
python ~/sandpit/compare_fasta.py
```


checked through all the pipeline scripts there is no coverage calcualtion for each of the amplicons. hence the lack of output in the /work/ folder

# Create Coverage data
To generate coverage using bedtools:
```bash
cd tailed_run_1
bedtools coverage -a /fastdata/ncov2019-arctic/nCoV-2019/V3/nCoV-2019.insert.bed -b ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_readMapping/20V00335729-C03_S19_L001.sorted.bam
MN908947.3      54      385     1       1       +       167150  331     331     1.0000000
MN908947.3      342     704     2       2       +       215051  362     362     1.0000000
MN908947.3      664     1004    3       1       +       59727   340     340     1.0000000
MN908947.3      965     1312    4       2       +       29940   347     347     1.0000000
.... etc
```

new script working
1. must use python3
2. runs bedtools coverage over the BAMs
3. uses multhithreading (48 cores)
4. creates a report in the root of the run folder 

```bash
geoffw@nbsvr484:~/sandpit/covid-extras$ sudo python3 coverage.py -r /mnt/NGS_DATA_at_Bristol/COVID/untailed_runs_1_and_2/
```



# Sort out Tailed_run_2 (96 plex)

move the fq folder and remove existing folders:

```
mv Data/Intensities/BaseCalls/fqs/ Data/Intensities/BaseCalls/wrong_fqs/
rm -r BRIS*
rm -r 20V*
```

redemultiplex:

```
docker run -v /largedata/share/MiSeqOutput2/210220_M03605_0235_000000000-JH7K2/:/run/ \
geoffw/centos_bcl2fastq2 \
bcl2fastq -R /run -o /run/Data/Intensities/BaseCalls \
--barcode-mismatches 0 --ignore-missing-bcls \
--ignore-missing-filter --ignore-missing-positions \
--sample-sheet /run/SampleSheet.csv
```

now run the arctic pipeline::

```
/largedata/share/MiSeqOutput2/210220_M03605_0235_000000000-JH7K2
NXF_VER=20.10.0 nextflow run /home/geoffw/sandpit/ncov2019-artic-nf \
-profile conda \
--cache /home/geoffw/miniconda3/envs/artic-ncov2019-illumina/
--illumina \
--prefix "tailed_run2_fixed" \
--ivarBed /fastdata/ncov2019-arctic/nCoV-2019/V3/nCoV-2019.bed \
--alignerRefPrefix /fastdata/ncov2019-arctic/nCoV-2019/V3/nCoV-2019.reference.fasta \
--directory /largedata/share/MiSeqOutput2/210220_M03605_0235_000000000-JH7K2/Data/Intensities/BaseCalls \
--outdir /largedata/share/MiSeqOutput2/210220_M03605_0235_000000000-JH7K2/ncov2019-arctic-nf_FIXED

```

get the fa's together for pangolin:

```
cat ncov2019-arctic-nf_FIXED/ncovIllumina_sequenceAnalysis_makeConsensus/*fa > tailed_run2_fixed_all.fa
conda activate pangolin
pangolin ncovIllumina_sequenceAnalysis_makeConsensus/tailed_run2_fixed_all.fa 
```

now run the new verification script:

```
python ~/sandpit/covid-extras/compare_pangolin.py \
-s SampleSheet.csv \
-c ~/temp_cog/BRIS_cog_2021-02-25_metadata.csv \
-p ./ncov2019-arctic-nf_FIXED/lineage_report.csv \
-o verification.csv

```

there are a few issues but overall we have a very good level of concordance!

```
geoffw@nbsvr484:/largedata/share/MiSeqOutput2/210220_M03605_0235_000000000-JH7K2$ grep False verification.csv 
4,BRIS-1855845,20V00299373,B.1.177.15,False,B.1.177
35,20V00335341,20V00335341,B.1.177.15,False,NA
36,20V00335341,20V00335341,B.1.177,False,NA
37,BRIS-25CE90,20V00335709,B.1.258.7,False,B.1.160
38,BRIS-25CF06,20V00335821,B.1.160,False,B.1.258.7
53,BRIS-1856659,20V60170512,B.1.1.74,False,B.1.1.189
54,BRIS-25AC4D,20V60171170,B.1,False,B.1.177
83,BRIS-25A2C3,20V00306843,None,False,B.1.177
84,BRIS-25A30C,20V00306981,None,False,B.1.177
85,BRIS-25A1D5,20V00309548,None,False,B.1.1.311
86,BRIS-25A1E4,20V00309636,None,False,B.1.177
87,BRIS-25CBD5,20V00324573,None,False,B.1.177
88,BRIS-25CB20,20V00332059,None,False,B.1.177
89,BRIS-25CE81,20V00333775,None,False,B.1.177
90,BRIS-25CEBE,20V00334302,None,False,B.1.177
91,BRIS-25CECD,20V00334807,None,False,B.1.177
92,BRIS-25CE36,20V00334872,None,False,B.1.177
93,BRIS-25CEAF,20V00335312,None,False,B.1.177
94,BRIS-1855B1F,20V60163241,None,False,B.1.160
95,BRIS-25A21E,20V70232659,None,False,B.1.177.9
```

# 384 plex run 
## Tailed runs 2,3,4 + 5:

Rsync and Save the new samplesheet:
```
rsync -azvP --include "*/" --include "*xml" \
--include "*csv" --include "*txt" --include "*bin" \
--include "*bcl" --include **"*bci"** --exclude "*" \
/RUN_FOLDERS/MiSeqOutput2/210302_M03605_0237_000000000-JJDN8 /largedata/share/MiSeqOutput2/

cd /largedata/share/MiSeqOutput2/210302_M03605_0237_000000000-JJDN8/
mv SampleSheet.csv SampleSheet.csv.wrong
cp /mnt/K/01\ NGS/NGS\ Validations/COVID-19\ ARTIC\ v3/Validation/Tailed\ Run\ 2-5\ replacement.csv .
cp Tailed\ Run\ 2-5\ replacement.csv SampleSheet.csv
```

### Re-demux:

```
docker run -v /largedata/share/MiSeqOutput2/210302_M03605_0237_000000000-JJDN8/:/run/ \
geoffw/centos_bcl2fastq2 \
bcl2fastq -R /run -o /run/Data/Intensities/BaseCalls \
--barcode-mismatches 0 --ignore-missing-bcls \
--ignore-missing-filter --ignore-missing-positions \
--sample-sheet /run/SampleSheet.csv
```

### Run the pipeline:
```
NXF_VER=20.10.0 nextflow run /home/geoffw/sandpit/ncov2019-artic-nf \
-profile conda \
--cache /home/geoffw/miniconda3/envs/artic-ncov2019-illumina/ \
--illumina \
--prefix "tailed_runs_2-5" \
--ivarBed /fastdata/ncov2019-arctic/nCoV-2019/V3/nCoV-2019.bed \
--alignerRefPrefix /fastdata/ncov2019-arctic/nCoV-2019/V3/nCoV-2019.reference.fasta \
--directory /largedata/share/MiSeqOutput2/210302_M03605_0237_000000000-JJDN8/Data/Intensities/BaseCalls \
--outdir /largedata/share/MiSeqOutput2/210302_M03605_0237_000000000-JJDN8/ncov2019-arctic-nf

Completed at: 05-Mar-2021 13:18:57
Duration    : 8m 7s
CPU hours   : 12.7
Succeeded   : 2'608
```
**Super FAST!!** set queue to 48 but it still went very quickly - unsure if throttling possible as Matt said.

get the fa's together for pangolin:

```
cat ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*fa > tailed_runs_2-5_all.fa
conda activate pangolin
pangolin tailed_runs_2-5_all.fa
conda deactivate
```

now run the new verification script:

```
python ~/sandpit/covid-extras/compare_pangolin.py \
-s SampleSheet.csv \
-c ~/temp_cog/BRIS_cog_2021-02-25_metadata.csv \
-p lineage_report.csv \
-o verification.csv

```

OK we have issues with the samples names - to avoid replicate names in the SS they've added a PREFIX!!
this needs to be removed for the verification to work correctly!
* Extra function to parse COG_ID in samplesheet to remove prefix to allow matching
* Added QC as well to improve level of information

re-ran the verification script after fixing then...
copied to network

```
python ~/sandpit/covid-extras/compare_pangolin.py -s SampleSheet.csv -c ~/temp_cog/BRIS_cog_2021-02-25_metadata.csv -p lineage_report.csv -q ncov2019-arctic-nf/tailed_runs_2-5.qc.csv -o verification.csv
Matches = 304
Errors = 76

sudo mkdir /mnt/NGS_DATA_at_Bristol/COVID/tailed_runs_2-5
sudo cp -r ncov2019-arctic-nf/ /mnt/NGS_DATA_at_Bristol/COVID/tailed_runs_2-5/.
sudo cp lineage_report.csv /mnt/NGS_DATA_at_Bristol/COVID/tailed_runs_2-5/.
sudo cp verification.csv /mnt/NGS_DATA_at_Bristol/COVID/tailed_runs_2-5/.
```

plot a boxplot of coverage vs match status!!

```python3
import pandas as pd
import matplotlib.pyplot as plt
df=pd.read_csv('verification.csv')
df.boxplot(by='match', column=['pct_covered_bases'])
plt.savefig('myplot.png')
```

## 4 failures:
Plan
1) download fastqs
2) run pipeline
3) compare fastas
4) run fastQC - has the sample degraded?
5) run my QC script to make summary
6) write script to get insert size from BAMS

### Cases to Download from ENA

* BRIS-1855845 (56%) BRIS-1855845 (90%) [B.1.177.15 better] ena_files.zip [ERR5077407]
* BRIS-1855B5B (59%) BRIS-1855B5B (63%) BRIS-1855B5B (64%) [B.1.1.74 -> B.1.1.151] ena_files(1).zip [ERR5081183]
* BRIS-1856659 (99%) BRIS-1856659 (99%) BRIS-1856659 (99%) BRIS-1856659 (99%) [B.1.1.74 -> B.1.1.189] ena_files(2).zip [ERR5070329]
* BRIS-25AC4D (67%) ena_files(3).zip [ERR4839203]

Copied to here:
* L:\Genetics\Analyser Data\Sequencing Data\NGS_DATA_at_Bristol\COVID\verification


### FastQC
run: sudo python
```python3
import os
import subprocess
import multithreading.dummy

FASTQC_CONTAINER = "geoffw/fastqc0.11.4"
FASTQC_EXE = "fastqc"
FASTQC_VERSION = "v0.11.4"

run_dir='/largedata/share/MiSeqOutput2/210302_M03605_0237_000000000-JJDN8'
mnts = "-v {}:/run".format(run_dir) 
files = os.listdir(os.path.join(run_dir, "Data/Intensities/BaseCalls"))
for fq in [fq for fq in files if fq.endswith("fastq.gz") and not fq.startswith("Undetermined")]:
      fastq = "/run/Data/Intensities/BaseCalls/"+fq
      cmd = "docker run "+mnts+" "+FASTQC_CONTAINER+" "+FASTQC_EXE+" "+fastq
      cmd +=" --outdir /run/FastQC"
      subprocess.call([ cmd ], shell=True)
```


## Get insert size
samtools flagstat

Run this over all BAM files!!!!!
```
sudo docker run --rm \
-v "$(pwd)":/run/ \
-v /fastdata/ncov2019-arctic/SARS-CoV-2/V3:/ref/ \
geoffw/picard1.67 \
java -jar /picard-tools-1.67/CollectInsertSizeMetrics.jar \
I=/run/4-20V80022587-E7_S230_L001.sorted.bam \
R=/ref/nCoV-2019.reference.fasta \
H=/run/4-20V80022587-E7_S230_L001.hist \
O=/run/4-20V80022587-E7_S230_L001.txt
```

Created a new sript to run this in parallel BOOOOOOOOM!!

```
python3 ~/sandpit/covid-extras/picard.py -a /largedata/share/MiSeqOutput2/210302_M03605_0237_000000000-JJDN8/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_readMapping/ -o insert_report.txt
```

now merge with other data:

```python3
import pandas as pd
run="/largedata/share/MiSeqOutput2/210302_M03605_0237_000000000-JJDN8"
insert=pd.read_csv(run+"/insert_report.txt")
ver=pd.read_csv(run+"/verification.csv")
final = pd.merge(left=ver, right=insert, left_on='WINPATH_ID', right_on='case')
del final['Unnamed: 0_x']
del final['Unnamed: 0_y']
final.to_csv(run+"/verification_insert.csv", index=False)
```

# Plot correlation
```python3
import pandas as pd
import matplotlib.pyplot as plt
df=pd.read_csv('verification_insert.csv')
df['colour']="Red"
df.loc[df.qc_pass==True, 'colour']="Green"
df.plot.scatter(y='MEDIAN_INSERT_SIZE', x='pct_covered_bases', c=df.colour)
plt.savefig('insert_coverage_scatter.png')
```

# Follow up Lineage mismatches!

### Create fasta file to investigate sample swap

```
cat verification/96plate_validation/BRIS-25CF06* > sample_swap_investigation.fa
cat tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*20V00335709* >> sample_swap_investigation.fa
cat verification/96plate_validation/BRIS-25CE90* >> sample_swap_investigation.fa
cat tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*20V00335821* >> sample_swap_investigation.fa
```

### Create Other 4 fasta files for investigation:

```
cat verification/96plate_validation/BRIS-1855B5B* > BRIS-1855B5B_investigation.fa
cat tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*20V60165216* >> BRIS-1855B5B_investigation.fa
cat verification/96plate_validation/BRIS-1856659* > BRIS-1856659_investigation.fa
cat tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*20V60170512* >> BRIS-1856659_investigation.fa
cat verification/96plate_validation/BRIS-1855845* > BRIS-1855845_investigation.fa
cat tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*20V00299373* >> BRIS-1855845_investigation.fa
cat verification/96plate_validation/BRIS-25AC4D* > BRIS-25AC4D_investigation.fa
cat tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/*20V60171170* >> BRIS-25AC4D_investigation.fa
```

> uploaded to: https://clades.nextstrain.org/

Updated the Excel workbook

### follow up BRIS-1856659 mismatch

Our 4 replicates are high quality and assigned B.1.1.74
however the data from Steph states a lineage of B.1.1.189
run locally with the fasta to check:

```
conda activate pangolin
pangolin BRIS-1856659_investigation.fa
conda deactivate
```

__Reference comes back as B.1.1.74 same as our samples!!__
Have checked the COG-UK metadata - and this means it must have been uploaded incorrectly!

# MetaData

1) New data parsed
2) Everything with Lab numbers (20V....)
3) log of interesting strains
4) 




