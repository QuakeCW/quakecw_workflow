import argparse
from jinja2 import Environment, FileSystemLoader
import os
from pathlib import Path
import shutil
import tempfile

from qcore.shared import exe

MAKE_VM_PBS_TEMPLATE= "make_vm.template"

def load_args():
    parser= argparse.ArgumentParser()
    parser.add_argument(
        "vm_params_yaml",type=str, help="Path to vm_params file (must include file name)"
    )
    parser.add_argument(
        "name",type=str, help="VM name")
    parser.add_argument(
        "--outdir",type=str, help="directory to write the VM data", default="."
    )

    parser.add_argument(
        "--ncores",type=int, help="Number of cores to use (1-68)", default=68)

    parser.add_argument(
        "--wallclock",type=int, help="Wallclock limit (1-48)",default=15)

    parser.add_argument(
        "--pbs_template",type=Path, help="PBS script template",default=Path(__file__).parent.resolve()/MAKE_VM_PBS_TEMPLATE)


    args = parser.parse_args()
    args.vm_params_yaml=Path(args.vm_params_yaml).resolve()
    #print(args.pbs_template)
    assert(args.vm_params_yaml.exists())
    

    return args

if __name__ == '__main__':
    args = load_args()

    outdir=Path(args.outdir).resolve()
    outdir.mkdir(parents=True,exist_ok=True)
    print(f"Created: {outdir}")


    print(f"Loaded: {args.vm_params_yaml}")
    new_vm_params_yaml = outdir/"vm_params.yaml"
    shutil.copyfile(args.vm_params_yaml,new_vm_params_yaml)
    print(f"Copied {args.vm_params_yaml.name} to {outdir}")

    # if args.pbs_template is in a different directory, things can get a little messy
    # we will make a temporary file that is a copy of the original args.pbs_template, 
    # and 
    CWD=Path().cwd()
    temp_handle, temp_template = tempfile.mkstemp(suffix=".template",dir=CWD)
    print(temp_template)
    shutil.copyfile(args.pbs_template,temp_template)

    env = Environment(loader=FileSystemLoader(CWD))
    pbs_template = env.get_template(Path(temp_template).name) # get_template wants to handle the filename only
    pbs_script = pbs_template.render(ncores=args.ncores,wallclock=f"{args.wallclock:02d}",vm_params_yaml=new_vm_params_yaml,output_dir=outdir,rel_name=args.name)
    os.close(temp_handle)
    os.remove(temp_template)

    MAKE_VM_PBS=str(args.pbs_template.name).replace(".template",".pbs")
    with open(outdir/MAKE_VM_PBS,"w") as f:
        f.write(pbs_script)
        f.write("\n")

    print(f"Generated: {outdir/MAKE_VM_PBS}")


    os.chdir(outdir)
    cmd=f"qsub -V -W umask=002 {outdir/MAKE_VM_PBS}"
    print(f"Submitted: {cmd}")
    res=exe(cmd,debug=False)
    job_id=res[0].strip()
    print(job_id)
