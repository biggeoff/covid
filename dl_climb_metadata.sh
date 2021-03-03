#!/bin/bash
cd /home/geoffw/temp_cog/
scp climb-covid19-woodwardg@bham.covid19.climb.ac.uk:/cephfs/covid/bham/results/phylogenetics/latest/public/*_metadata.csv .
for csvfile in *.csv
do
    echo "Processing ${csvfile}"
    grep BRIS $csvfile > "BRIS_"${csvfile}
done
# copy to network completed by separate cronjob run by root in 15 minutes.
