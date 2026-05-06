#!/bin/bash

# Get the directory where the current script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

#get run_name from $1

if [[ $# -lt 1 ]]; then
    echo "please provide the sim_dir"
    exit 1
fi

sim_dir=$1
#bb_run_name=$2
#srf_name=$3

cd $sim_dir
fd_ll=`python -c "from qcore import utils; p = utils.load_sim_params('sim_params.yaml'); print(p['FD_STATLIST'])"`

bb_sim_dir=$sim_dir/BB
bb_acc_dir=$bb_sim_dir/Acc
bb_bin=$bb_acc_dir/BB.bin

ls $bb_bin 2> /dev/null
if [[ $? != 0 ]]; then
    echo "$bb_sim_dir: have not yet run"
    exit 1
fi

#get the len of fd_ll
#fd_count=$(expr `cat $fd_ll | wc -l` \* 3)

#check the len(fd_ll) == len(hf.stations)
#check station names are not empty
python $SCRIPT_DIR/test_binary.py $bb_bin $fd_ll bb --verbose

