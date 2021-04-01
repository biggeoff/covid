# COG - COVID19 Sequencing Bioinformatics
## How to set up the compute environment
### Hardware
<hr>
To run inline with existing NGS workflows in the laboratory we will be creating the environment on NBSVR484 server. A specialised compute server with 96 cores and 384GB of RAM. However Miseq data is relatively small and could be processed on a well powered desktop computer.

> Minimum requirments:
>  * 4-8 cores (recent i7 processor)
>  * 16 GB RAM
>  * Windows 10 with WSL ()
>    * Windows Subsystem for Linux activated (requires administrator privileges)
>    * Ubuntu >= 16.04

### Environment
<hr>

To set up the virtual environment we first need to install Conda. We'll download and install miniconda using all defaults:

```
geoffw@nbsvr484:~/sandpit/$ wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
geoffw@nbsvr484:~/sandpit/$ chmod 775 Miniconda3-latest-Linux-x86_64.sh
geoffw@nbsvr484:~/sandpit/$ ./Miniconda3-latest-Linux-x86_64.sh
```

> type "yes" at the prompts

Once installed make sure to deactivate the base environment, so that other users don't get a shock when logging in. (Otherwise Python version 3.8.5 will launch by default)

```
geoffw@nbsvr484:~/sandpit/$ conda config --set auto_activate_base false
```

Now we'll clone the git repository and build the conda virtual environment for Illumina sequencing:

```
geoffw@nbsvr484:~/sandpit/$ git clone https://github.com/connor-lab/ncov2019-artic-nf.git
geoffw@nbsvr484:~/sandpit/$ cd ncov2019-artic-nf
geoffw@nbsvr484:~/sandpit/ncov2019-artic-nf$ conda env create -f environments/illumina/environment.yml
```

> It will take quite some time to download, install and manage all python packages

Now the main requirement is the workflow language NextFlow, which is newer than the version we currently use for the RNA pipeline:
> 

### Test:
<hr>
Once commpleted test the new conda environment:

```
geoffw@nbsvr484:~/sandpit/ncov2019-artic-nf$ conda activate artic-ncov2019-illumina
(artic-ncov2019-illumina) geoffw@nbsvr484:~/sandpit/ncov2019-artic-nf$ 
```

the command prompt should now give you the name of the activated environment in parentheses.

To deactivate and return to normal host environment use the following:
```
(artic-ncov2019-illumina) geoffw@nbsvr484:~/sandpit/ncov2019-artic-nf$ conda deactivate
geoffw@nbsvr484:~/sandpit/ncov2019-artic-nf$
```


# Pangolin

Lets install Pangolin in my sandpit for testing.

```bash
geoffw@nbsvr484:~/sandpit/$ cd pangolin
geoffw@nbsvr484:~/sandpit/pangolin$ conda env create -f environment.yml
geoffw@nbsvr484:~/sandpit/pangolin$ conda activate pangolin
(pangolin) geoffw@nbsvr484:~/sandpit/pangolin$ python setup.py install
```
test
```bash
(pangolin) geoffw@nbsvr484:~/sandpit/pangolin$ pangolin -v
pangolin 2.2.3
(pangolin) geoffw@nbsvr484:~/sandpit/pangolin$ pangolin -pv
pangoLEARN 2021-02-12
(pangolin) geoffw@nbsvr484:~/sandpit/pangolin$ pangolin -lv
usage: pangolin <query> [options]
pangolin: error: unrecognized arguments: -lv
```

OK lets' create a fasta file for the latest run and test:
```bash
cd /largedata/share/MiSeqOutput2/210212_M03605_0232_000000000-JH582/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus
cat *.fa > all_tailed_run1.fa
pangolin all_tailed_run1.fa
```
all working perfectly.


```
conda deactivate
```

# NextClade

further QC information can be gleaned from nextclade
we have used the online version for genome visualisation to help with validation

> docker pull nextstrain/nextclade

test run:

```
docker run --rm \
-v /mnt/NGS_DATA_at_Bristol/COVID/tailed_runs_2-5/ncov2019-arctic-nf/ncovIllumina_sequenceAnalysis_makeConsensus/:/in/ \
-v /mnt/NGS_DATA_at_Bristol/COVID/tailed_runs_2-5/nextclade/:/out/ \
nextstrain/nextclade nextclade \
-i '/in/4-20V80022587-E7_S230_L001.primertrimmed.consensus.fa' \
-o '/out/4-20V80022587_nextclade.json'
```

# COV-ERT/type_variants for key mutation reporting

https://github.com/cov-ert/type_variants
* COV-ERT type_variants used by CLIMB
    * get running locally to get results without having to wait


clone git repo and test:
```
geoffw@nbsvr484:sandpit$ git clone https://github.com/cov-ert/type_variants.git
geoffw@nbsvr484:sandpit$ cd type_variants/
geoffw@nbsvr484:type_variants$ python3 type_variants.py --fasta-in query.fasta --variants-config artic_config.csv --reference MN908947.fa --variants-out out.withgenotypes.csv --append-genotypes
```
Created a config file with the variatns output by the arctic pipeline as well as 2 further loci:

```
# Arctic
aa:S:D614G
aa:S:N439K
aa:orf1ab:P4715L
aa:S:Y453F
aa:S:E484K
aa:S:N501Y
aa:orf1ab:T1001I
aa:S:P681H
aa:orf8:Q27*
del:21765:6
# Local extras
aa:S:S494P
aa:S:K417T
```

integrate to `covid_extras.py`



# Install NAAAAVI 

https://github.com/SamStudio8/naaaavi/

Create a set of IDs for our PHESW code - superceeding BRIS 
```
geoffw@nbsvr484:sandpit$ git clone https://github.com/SamStudio8/naaaavi
geoffw@nbsvr484:sandpit$ cd naaaavi
geoffw@nbsvr484:sandpit$ pip3 install naaaavi
geoffw@nbsvr484:sandpit$ naaaavi generate --alphabet zbase32 --checksum luhn_mod_n --size 5 --rejectors max_repeats:2 min_unique:3 ismp_flips: better_profanity: not_exclusive:0123456789aAbBcCdDeEfF --prefix 'PHESW-' --upper -n 250
```

OK that's working nicely... let's bang out 250

```
naaaavi generate --alphabet zbase32 --checksum luhn_mod_n --size 6 --rejectors max_repeats:2 min_unique:3 ismp_flips: better_profanity: not_exclusive:0123456789aAbBcCdDeEfF --prefix 'PHESW-' --upper -n 250 > PHESW_first_250_codes.tsv
```

When we need to create more simply use the `--start-code` swithc with the final code from the previous output :

### 01/04/2021
second batch
```
naaaavi generate --alphabet zbase32 --checksum luhn_mod_n --size 6 --rejectors max_repeats:2 min_unique:3 ismp_flips: better_profanity: not_exclusive:0123456789aAbBcCdDeEfF --prefix 'PHESW-' --upper -n 501 --start-code PHESW-YYBYKC > PHESW_second_500_codes.tsv
```
Deleted the first row! (as it is a duplicate of the final row of the last batch)

