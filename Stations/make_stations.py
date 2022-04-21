import argparse
import pandas as pd

from pathlib import Path
import yaml
import tempfile
from qcore.shared import exe
from VM.gen_coords import gen_coords

def load_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "vm_params_yaml",type=str, help="Path to vm_params.yaml including file name",default="."
    )
    parser.add_argument(
        "--outdir",type=str, help="directory to write the output ll file",default="."
    )
    parser.add_argument(
        "--name",type=str, help="name of the output .ll/.vs30 file",default="stats"
    )
    parser.add_argument(
        "--real_stats",type=str,help="Real station file to append to virtual stations. (lon lan name) format each line", default=None)

    args = parser.parse_args()

    vm_params_yaml = Path(args.vm_params_dir)/ "vm_params.yaml"
    assert(vm_params_yaml.exists())

    if args.real_stats is not None:
        args.real_stats=Path(args.real_stats)
        assert(args.real_stats.exists())

    assert(Path(args.outdir).is_dir())

    with open(vm_params_yaml,'r') as file:
        args.params=yaml.safe_load(file)

    return args

if __name__ == '__main__':
    args = load_args()
    #print(args.params)
    params = args.params
    original_hh = params['hh']
    params['hh']=2.0
    params['flo']=0.05
    params['nx']=int(params['nx']*original_hh/params['hh'])
    params['ny']=int(params['ny']*original_hh/params['hh'])
    params['nz']=int(params['nz']*original_hh/params['hh'])
    params['sufx']="_rt01-h2.000"
    params['GRIDFILE'] = params['GRIDFILE'].replace("0.100","2.000")
    params['GRIDOUT'] = params['GRIDOUT'].replace("0.100","2.000")
    params['MODEL_BOUNDS'] = params['MODEL_BOUNDS'].replace("0.100","2.000")
    params['MODEL_COORDS'] = params['MODEL_COORDS'].replace("0.100","2.000")
    params['MODEL_PARAMS'] = params['MODEL_PARAMS'].replace("0.100","2.000")


    with tempfile.TemporaryDirectory(dir=args.vm_params_dir) as tmpdir:
        print('created temp dir', tmpdir)
        new_vm_params_yaml=Path(tmpdir)/"vm_params.yaml"
        with open(new_vm_params_yaml,"w") as file:
            documents = yaml.dump(params, file)
        gen_coords(tmpdir)
        stats=pd.read_csv(Path(tmpdir)/"model_coords_rt01-h2.000",delimiter=" ",index_col=None,usecols=[3,8],names=['lon','lat'])
        stats['name']=["{:06X}".format(x) for x in range(len(stats))]
       
        if args.real_stats is not None:
            real_stats=pd.read_csv(args.real_stats,sep=' ',index_col=None, names=['lon','lat','name'])
        else:
            real_stats=None

        all_stats=pd.concat([stats,real_stats])
        all_stats.lat = all_stats.lat.round(5)
        all_stats.lon = all_stats.lon.round(5)
        all_stats.to_csv(Path(args.outdir)/f"{args.name}.ll",sep=' ',header=None,index=None)

        res=exe(f"python extract_Vs30.py {Path(args.outdir)/args.name}.ll",debug=False)
        print(res[0])



