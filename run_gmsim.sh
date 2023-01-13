#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Missing argument: .yaml file"
    exit 2
fi
gmsim_yaml=$1

arr=($(cat $1|grep "sim_root_dir:"))
sim_root_dir=${arr[1]}
arr=($(cat $1|grep "workflow:"))
workflow=${arr[1]}
arr=($(cat $1|grep "n_max_retries:"))
n_max_retries=${arr[1]}

echo "sim_root_dir: $sim_root_dir"
echo "workflow: $workflow"
echo "n_max_retries: $n_max_retries"

script=$workflow/"workflow/automation/execution_scripts/run_cybershake.py"
cd $sim_root_dir

cmd="python $script `pwd` $USER `pwd`/task_config.yaml --n_max_retries $n_max_retries --sleep_time 1500"
echo $cmd
$cmd



