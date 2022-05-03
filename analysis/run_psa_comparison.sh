#!/bin/bash
ObsDir=Obs_Acc
cd $ObsDir
files=`ls *.000 |awk -F. '{print $1}'`
cd -

outdir_root=psa_comparison
rm -rf $outdir_root

#python $gmsim/IM_calculation/IM_calculation/scripts/calculate_ims.py -i Pohang -t o 2017319_Acc_qcore/ a -o ./Observed_IM -c 000 090 geom  -s

for run in `cat RELS.txt`;
do
    echo $run
    python $gmsim/visualization/im/psa_comparisons.py  --run-name ${run} --stations `echo $files`  --imcsv  $SCRATCH/gmsim/RunFolder/${run}/Runs/${FAULT}/${REL}/IM_calc/${REL}.csv Sim --imcsv Obs_IM/${REL}.csv Obs
    outdir=$outdir_root/${run}
    mkdir -p $outdir
    mv pSA_comp*.png $outdir

done
rm -f psa.tgz
tar zcvf psa.tgz $outdir_root



