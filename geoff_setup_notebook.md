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





