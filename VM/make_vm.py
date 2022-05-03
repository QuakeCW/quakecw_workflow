import argparse
from jinja2 import Environment, FileSystemLoader
import os
from pathlib import Path
import shutil

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
        "--pbs_template",type=str, help="PBS script template",default=MAKE_VM_PBS_TEMPLATE)


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

    env = Environment(loader=FileSystemLoader(Path(__file__).parent.resolve()))
    pbs_template = env.get_template(Path(args.vm_params_yaml).resolve())
    pbs=pbs_template.render(ncores=args.ncores,wallclock=f"{args.wallclock:02d}",vm_params_yaml=new_vm_params_yaml,output_dir=outdir,rel_name=args.name)

    MAKE_VM_PBS=args.pbs_template.replace(".template",".pbs")
    with open(outdir/MAKE_VM_PBS,"w") as f:
        f.write(pbs)
        f.write("\n")

    print(f"Generated: {outdir/MAKE_VM_PBS}")


    os.chdir(outdir)
    cmd=f"qsub -V {outdir/MAKE_VM_PBS}"
    print(f"Submitted: {cmd}")
    res=exe(cmd,debug=False)
    job_id=res[0].strip()
    print(job_id)
