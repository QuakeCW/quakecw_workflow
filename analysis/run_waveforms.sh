#!/bin/bash
zipfileName=waveforms_${REL}.tgz
ObsAccDir=Obs_Acc
ObsVelDir=Obs_Vel

echo $ObsAccDir
cd $ObsAccDir

files=`ls *.000 |awk -F. '{print $1}'`
cd -

rm -rf waveforms_*

for x in `cat RELS.txt`;
do
  echo $x
  inputBB=$SCRATCH/gmsim/RunFolder/${x}/Runs/${FAULT}/${REL}/BB/Acc/BB.bin
  echo $inputBB
  echo $ObsAccDir
  cmd="python $gmsim/visualization/waveform/waveforms.py --waveforms ${ObsAccDir} Obs  --waveforms ${inputBB} Sim -t 90 --acc --no-amp-normalize --stations ${files}"
  echo $cmd
  $cmd
  rm -rf waveforms_acc_${x}
  mv waveforms waveforms_acc_${x}
  echo $ObsVelDir
  cmd="python $gmsim/visualization/waveform/waveforms.py --waveforms ${ObsVelDir} Obs  --waveforms ${inputBB} Sim -t 90 --no-amp-normalize --stations ${files}"
  echo $cmd
  $cmd
  rm -rf waveforms_vel_${x}
  mv waveforms waveforms_vel_${x}

done

mkdir waveforms
mv waveforms_* waveforms
rm -f $zipfileName 
tar zcvf $zipfileName waveforms
