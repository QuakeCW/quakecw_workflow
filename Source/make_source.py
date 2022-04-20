import argparse
from datetime import datetime
from  jinja2 import Environment, FileSystemLoader
import os
from pathlib import Path
import pprint
import shutil

import yaml
from qcore.shared import exe

SET_SRF_PARAMS_TEMPLATE="setSrfParams.template"
SRF_CONFIG_TEMPLATE="srf_config.template"
CREATE_SRF="createSRF.py"

def load_args():
    parser= argparse.ArgumentParser()
    parser.add_argument(
        "yaml_file",type=str, help="source yaml file"
    )

    args = parser.parse_args()
    assert(Path(args.yaml_file).exists())
    with open(Path(args.yaml_file),'r') as file:
        args.params=yaml.safe_load(file)


    return args

def main():
    args = load_args()
    params=args.params

    outdir=Path(params['SOURCE_DATA_DIR'])
    outdir.mkdir(parents=True, exist_ok=True)
    
    # make setSrfParams.py from source.yaml and the template
    thisdir=Path(__file__).parent.resolve()
    env=Environment(loader=FileSystemLoader(thisdir))

    setSrfParams_template=env.get_template(SET_SRF_PARAMS_TEMPLATE)
    setSrfParams=setSrfParams_template.render(fault=params['FAULT'],fault_type=params['TYPE'],lat=params['LAT'],lon=params['LON'],depth=params['DEPTH'],mag=params['MAG'],stk=params['STK'],dip=params['DIP'],rak=params['RAK'],dt=params['DT'])
    with open(outdir/SET_SRF_PARAMS_TEMPLATE.replace(".template",".py"),"w") as f:
        f.write(setSrfParams)
        f.write("\n")
   
    # make srf_config.py from source.yaml and the template 
    srf_config_template=env.get_template(SRF_CONFIG_TEMPLATE)
    srf_config=srf_config_template.render(velocity_model=params['VELOCITY_MODEL'])
    with open(outdir/SRF_CONFIG_TEMPLATE.replace(".template",".py"),"w") as f:
        f.write(srf_config)
        f.write("\n")
   
    prev_wd=os.getcwd() 
    shutil.copyfile(thisdir/CREATE_SRF,outdir/CREATE_SRF)
    os.chdir(outdir)
    print("Executing createSRF.py")
    res=exe(f"python {CREATE_SRF}",debug=False)
    print(res[0])
    print(res[1])
    os.chdir(prev_wd)

if __name__ == "__main__":
    main()
