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

Tested access to CLIMB:
```
geoffw@nbsvr484:~/$ cat test_upload.txt 
testing connection from NBT NHS Trust - Geoff Woodward Bioinformatics from server NBSVR484 [10.229.248.19]
Proposed pathway for uploading Arctic COVID sequencing data from MiSeq platform
geoffw@nbsvr484:~/$ scp test_upload.txt climb-covid19-woodwardg@bham.covid19.climb.ac.uk:upload
test_upload.txt                                        100%  187   18.3KB/s    00:00
```

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


Install BioPython...
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