import argparse
import pandas as pd

from pathlib import Path
import yaml
#from tempfile import mkdtemp
from tempfile import TemporaryDirectory
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

    parser.add_argument(
        "--grid_size",type=float,help="Grid size. Distance between two neighbouring stations", default=2.0)


    args = parser.parse_args()

    args.vm_params_yaml = Path(args.vm_params_yaml)
    assert(args.vm_params_yaml.exists())

    if args.real_stats is not None:
        args.real_stats=Path(args.real_stats)
        assert(args.real_stats.exists())

    Path(args.outdir).mkdir(parents=True,exist_ok=True)

    #assert(Path(args.outdir).is_dir())

    with open(args.vm_params_yaml,'r') as file:
        args.params=yaml.safe_load(file)

    return args

if __name__ == '__main__':
    args = load_args()
    #print(args.params)
    params = args.params
    original_hh = params['hh']
    new_hh = args.grid_size
    params['hh']=new_hh
    params['flo']=1./new_hh
    params['nx']=int(params['nx']*original_hh/new_hh)
    params['ny']=int(params['ny']*original_hh/new_hh)
    params['nz']=int(params['nz']*original_hh/new_hh)
    params['sufx']=f"_rt01-h{new_hh:.3f}"
    params['GRIDFILE'] =f"./gridfile{params['sufx']}"
    params['GRIDOUT'] = f"./gridout{params['sufx']}"
    params['MODEL_BOUNDS'] = f"./model_bounds{params['sufx']}"
    params['MODEL_COORDS'] = f"./model_coords{params['sufx']}"
    params['MODEL_PARAMS'] = f"./model_params{params['sufx']}"

    with TemporaryDirectory(dir=args.vm_params_yaml.parent) as tmpdir:

#    tmpdir = mkdtemp(dir=args.vm_params_yaml.parent) # use this instead of above for debug
#    tmpdir=Path(tmpdir)

        print('created temp dir', tmpdir)
        new_vm_params_yaml=Path(tmpdir)/"vm_params.yaml"
        with open(new_vm_params_yaml,"w") as file:
            documents = yaml.dump(params, file)
        gen_coords(tmpdir)
        csv_file=Path(tmpdir)/f"model_coords{params['sufx']}"
        stats=pd.read_csv(csv_file,delimiter=" ",index_col=None,usecols=[3,8],names=['lon','lat'], engine='python')
        stats['name']=["{:06X}".format(x) for x in range(len(stats))]
       
        if args.real_stats is not None:
            real_stats=pd.read_csv(args.real_stats,sep=' ',index_col=None, names=['lon','lat','name'], engine='python')
        else:
            real_stats=None

        all_stats=pd.concat([stats,real_stats])
        all_stats.lat = all_stats.lat.round(5)
        all_stats.lon = all_stats.lon.round(5)
        all_stats.to_csv(Path(args.outdir)/f"{args.name}.ll",sep=' ',header=None,index=None)
        cmd=f"python {Path(__file__).parent.resolve()}/extract_Vs30.py {Path(args.outdir)/args.name}.ll"
        #print(cmd)
        res=exe(cmd,debug=False)
        print(res[0])



