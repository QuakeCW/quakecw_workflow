#!/bin/bash

outdir=im_plots

rm -rf $outdir
for run in `cat RELS.txt`; 
do 
    im_plot=$SCRATCH/gmsim/RunFolder/${run}/Runs/${FAULT}/${REL}/verification/IM_plot/geom/non_uniform_im;
    echo $im_plot;
    mkdir -p $outdir/$run;
    cp -r $im_plot/* $outdir/$run;
done
rm -f im_plots.tgz
tar zcvf im_plots.tgz $outdir
