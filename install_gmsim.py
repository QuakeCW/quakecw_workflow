import argparse
from datetime import datetime
from  jinja2 import Environment, FileSystemLoader

from pathlib import Path
import pprint
import shutil

import yaml

from qcore import qclogging
from qcore.shared import exe
from qcore.utils import load_py_cfg

from qcore.constants import (
    TIMESTAMP_FORMAT,
    ROOT_DEFAULTS_FILE_NAME
)


LOG_FILE_NAME = "install_quakecw_log_{}.txt"
FAULT_LIST="fault_list.txt"
TASK_CONFIG="task_config.yaml"
INSTALL_PBS="install.pbs"
PBS_TEMPLATE="serial.template"

def load_args():
    parser= argparse.ArgumentParser()
    parser.add_argument(
        "yaml_file",type=str, help="gmsim yaml file"
    )
    parser.add_argument(
        "--console",help="Run directly in console, not submitted as a job", action="store_true")

    args = parser.parse_args()
    assert(Path(args.yaml_file).exists())
    with open(Path(args.yaml_file),'r') as file:
        args.params=yaml.safe_load(file)


    return args

def copy_data(src,dest,logger,is_copy=False):
    if dest.exists():
        if dest.is_symlink():
            dest.unlink()
        else:
            shutil.rmtree(dest)

    if is_copy:
        #copy files
        shutil.copytree(src,dest)
        logger.debug(f"{src} is copied to {dest}")
    else:
        #create symbolic link
        dest.symlink_to(Path(src),target_is_directory=True)
        logger.debug(f"{src} is symbolic linked {dest}")

def main():
    logger = qclogging.get_logger()
    args = load_args()
    qclogging.add_general_file_handler(logger, LOG_FILE_NAME.format(datetime.now().strftime(TIMESTAMP_FORMAT)))

    params = args.params
    #print(params)

    # create sim_root_dir
    sim_root_dir=Path(params["sim_root_dir"])
    sim_root_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"{params['sim_root_dir']} created")
    
    assert(Path(params["source_data"]).exists()),f"Source data not found at {params['source_data']}"

    data_dir = sim_root_dir / "Data"
    source_dir = data_dir / "Sources"
    source_dir.mkdir(parents=True,exist_ok=True)
    
    source_fault_dir = source_dir/params["fault_name"]
    copy_data(params["source_data"],source_fault_dir,logger,params["copy_source_data"])

    vm_dir = data_dir / "VMs"
    vm_dir.mkdir(parents=True, exist_ok=True)
    vm_fault_dir = vm_dir/params["fault_name"]
    copy_data(params["vm_data"],vm_fault_dir,logger,params["copy_vm_data"])

    #fault_list
    num_rels=len(list(source_fault_dir.glob("Srf/*.srf")))
    with open(sim_root_dir/FAULT_LIST,"w") as f:
        line=f"{params['fault_name']} {num_rels}r\n"
        f.write(line)
        print(line)

    logger.debug(f"{FAULT_LIST} created")
    
    shutil.copyfile(Path(__file__).parent.resolve()/TASK_CONFIG,sim_root_dir/TASK_CONFIG)
    logger.debug(f"{TASK_CONFIG} is added to {sim_root_dir}")

    cmd=f"python {params['workflow']}/workflow/automation/install_scripts/install_cybershake.py {sim_root_dir} {sim_root_dir/FAULT_LIST} {Path(params['gmsim_template']).name} --stat_file_path {params['stat_file']} --keep_dup_station"

    if not args.console:
        env = Environment(loader=FileSystemLoader(Path(__file__).parent.resolve()))
        pbs_template = env.get_template(PBS_TEMPLATE)
        pbs=pbs_template.render(name=f"install_{params['fault_name']}", cmd=cmd)
       
        logger.debug(f"{INSTALL_PBS} created") 
        with open(sim_root_dir/INSTALL_PBS,"w") as f:
            f.write(pbs)
            f.write("\n")
        
        res=exe(f"qsub -V {sim_root_dir/INSTALL_PBS}",debug=False)
        job_id=res[0].strip()
        print(job_id)
        logger.debug(f"{job_id} submitted")

    else:
        res=exe(cmd,debug=False)
        print(res[0])
        


    print("================================")
    print("             Source")
    print("================================")

    setSrfParams=source_fault_dir/"setSrfParams.py"
    assert(setSrfParams.exists())
    print(setSrfParams)
    srfParams=load_py_cfg(str(setSrfParams))
    
    for p in ['LAT','LON','DEPTH','MAG','STK','DIP','RAK','DT']:
        print(f"{p}: {srfParams[p]}")

    print("================================")
    print("             VM")
    print("================================")
    
    vm_params_file=vm_fault_dir/"vm_params.yaml"
    assert(vm_params_file)
    print(vm_params_file)

    with open(vm_params_file,'r') as file:
        vm_params=yaml.safe_load(file)
    pprint.pprint(vm_params) 

    print("================================")
    print(f"       GMSIM template")
    print("================================")
    root_default_file=Path(params['gmsim_template'])/ROOT_DEFAULTS_FILE_NAME
    print(root_default_file)
    assert(root_default_file)

    with open(root_default_file,'r') as file:
        root_defaults_params=yaml.safe_load(file)
    pprint.pprint(root_defaults_params)

    print(f"Simulation installed at {sim_root_dir}")
    print(f"Run with : python run_gmsim.sh {Path(args.yaml_file).resolve()}")
if __name__ == "__main__":
    main()
