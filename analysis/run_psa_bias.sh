#!/bin/bash
ObsDir=Obs_Acc
cd $ObsDir
files=`ls *.000 |awk -F. '{print $1}'`
cd -

outdir_root=psa_bias
rm -rf $outdir_root

#python $gmsim/IM_calculation/IM_calculation/scripts/calculate_ims.py -i Pohang -t o 2017319_Acc_qcore/ a -o ./Observed_IM -c 000 090 geom  -s

for run in `cat RELS.txt`;
do
    echo $run

    outdir=$outdir_root/${run}
    mkdir -p $outdir

    python $gmsim/visualization/im/psa_bias.py  --run_name ${run} -o $outdir  --imcsv  $SCRATCH/gmsim/RunFolder/${run}/Runs/${FAULT}/${REL}/IM_calc/${REL}.csv Sim --imcsv Obs_IM/${REL}.csv Obs
#    mv pSA_comp*.png $outdir

done
rm -f psai_bias.tgz
tar zcvf psa_bias.tgz $outdir_root



