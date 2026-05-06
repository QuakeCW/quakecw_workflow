#!/bin/bash

#get run_name from $1

if [[ $# -lt 1 ]]; then
    echo "please provide the sim_dir, and srf_name"
    exit 1
fi

sim_dir=$1
#hf_run_name=$2
#srf_name=$3

cd $sim_dir
fd_ll=`python -c "from qcore import utils; p = utils.load_sim_params('sim_params.yaml'); print(p['FD_STATLIST'])"`

hf_sim_dir=$sim_dir/HF
hf_acc_dir=$hf_sim_dir/Acc
hf_bin=$hf_acc_dir/HF.bin
hf_log=$hf_acc_dir/HF.log

ls $hf_bin 2> /dev/null
if [[ $? != 0 ]]; then
    echo "$hf_sim_dir: have not yet run"
    exit 1
fi

SKIP_ZERO=""

# Check HF log for successful completion
if [[ -f $hf_log ]]; then
    if tail -5 "$hf_log" | grep -q "Simulation completed and size verified"; then
        echo "HF simulation completed and size verified"
	SKIP_ZERO="--skip-zero-check"
    else
        echo "ERROR: HF.log exists but does not contain 'Simulation completed and size verified' in last 5 lines"
        tail -5 "$hf_log"
        exit 1
    fi
else
    echo "ERROR: HF.log not found at $hf_log"
    exit 1
fi

#get the len of fd_ll
#fd_count=$(expr `cat $fd_ll | wc -l` \* 3)

#check the len(fd_ll) == len(hf.stations)
#check station names are not empty
echo $fd_ll
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python $SCRIPT_DIR/test_binary.py $hf_bin $fd_ll hf --verbose $SKIP_ZERO
