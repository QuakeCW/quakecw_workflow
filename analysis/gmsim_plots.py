import argparse
import datetime
from pathlib import Path
import shutil
import yaml
from qcore.shared import exe

STATION_LIST="station.list"

def load_args():
    parser=argparse.ArgumentParser()
    parser.add_argument(
        "--gmsim_yaml", help="Path to gmsim.yaml file", type=Path, action="append")

    parser.add_argument(
        "--obs", help="Path to Obs data, must include Obs_Acc,Obs_Vel and Obs_IM directories", type=Path,)

    parser.add_argument(
        "--outdir",type=Path, help="Directory to store plot results", default=Path().cwd()/"plots",)

    parser.add_argument(
        "--time", type=int, help="Length of waveform in seconds", default=90,)

    parser.add_argument(
        "--station_list", type=Path, help="A file containing name of station each line")
    parser.add_argument(
       "--skip_waveforms", action="store_true",dest="skip_waveforms",help="Set this flag if you wish to skip plotting wavforms",default=False)
    parser.add_argument(
       "--skip_psa_comparisons", action="store_true",dest="skip_psa_comparisons",help="Set this flag if you wish to skip psa comparisons",default=False)

    parser.add_argument(
       "--skip_psa_bias", action="store_true",dest="skip_psa_bias",help="Set this flag if you wish to skip psa bias",default=False)

    parser.add_argument(
       "--skip_implots", action="store_true",dest="skip_implots",help="Set this flag if you wish to skip collecting implots",default=False)


    args = parser.parse_args()

    if args.outdir.exists():
        print(f"WARNING: {args.outdir} already exists")
        dt=datetime.datetime.fromtimestamp(args.outdir.stat().st_ctime)
        timestamp=dt.strftime("%Y%m%d_%H%M%S")
        print(timestamp)
        outdir_moveto=args.outdir.parent / f"{args.outdir.name}_{timestamp}"
        print(f"Relocated to {outdir_moveto}")
        shutil.copytree(args.outdir,outdir_moveto)
        shutil.rmtree(args.outdir)
        

    # validating gmsim_yaml
    for gmsim_yaml in args.gmsim_yaml:
        assert gmsim_yaml.exists(), f"{gmsim_yaml} is not present"

    # validating obs
    if args.obs is not None:
        for subdir in ["Obs_Vel", "Obs_Acc", "Obs_IM"]:
            assert (args.obs / subdir).exists(), f"{args.obs}/{subdir} is not present"
        else:
            print(f"##### Observation data: {args.obs}")

    # examining the contents of gmsim_yaml
    gmsim_configs = []
    for gmsim_yaml in args.gmsim_yaml:
        with(open(gmsim_yaml,'r')) as file:
            gmsim_configs.append(yaml.safe_load(file))

    fault_names = []
    bb_list = []
    imcsv_list = []
    implots_list = []
    for gmsim_conf in gmsim_configs:
        sim_root_dir = gmsim_conf['sim_root_dir']
        fault_name = gmsim_conf['fault_name']
        fault_names.append(fault_name)
        runs_fault_dir = Path(sim_root_dir) / "Runs" / fault_name
        bb_path = runs_fault_dir.glob("*/BB/Acc/BB.bin")
        for bp in bb_path:
            bb_list.append((Path(sim_root_dir).name,str(bp)))
        imcsv_path = runs_fault_dir.glob("*/IM_calc/*.csv")
        for imp in imcsv_path:
            imcsv_list.append((Path(sim_root_dir).name,str(imp)))

        implots_path = runs_fault_dir.glob("*/verification/IM_plot/geom/non_uniform_im")
        for imp in implots_path:
            implots_list.append((Path(sim_root_dir).name,str(imp)))
       
        args.gmsim_env = Path(gmsim_conf['workflow']).parent

    args.bb_list=bb_list
    for i, bb in enumerate(bb_list):
        print(f"##### Sim BB (Acc) {i+1}: {bb}")

    args.imcsv_list=imcsv_list
    for i, im in enumerate(imcsv_list):
        print(f"##### IM CSV {i+1}: {im}")

    args.implots_list=implots_list
    for i, im in enumerate(implots_list):
        print(f"##### IM Plots {i+1}: {im}")

    assert(len(set(fault_names))==1), f"All fault names should be the same: {fault_names}"
  
    station_list=[]
    if args.station_list is None: #station_list is not specified
        #If obs is specified
        if args.obs is not None:
            print("##### Stations extracted from Observation data")
            station_000s=(args.obs/"Obs_Acc").glob("*.000")
            for s0 in station_000s:
                st_name = Path(str(s0)).stem
                station_list.append(st_name)
        else:
            station_list_file = Path(__file__).parent.resolve() / STATION_LIST
            args.station_list = station_list_file
            print(f"##### Warning: Station list not specified: Trying the default station list: {station_list_file}")
               
    if args.station_list is not None:
        assert args.station_list.exists(), f"{args.station_list} is not present"
        with open(args.station_list,"r") as f:
            station_list=f.readlines()
        station_list=[x.strip("\n") for x in station_list]
         
    station_list.sort()
    args.station_list_str=" ".join(station_list)
    print(f"##### Station list: {args.station_list_str}")

     
    return args


if __name__ == '__main__':
    args= load_args()

#    print(args)


    #waveforms
    if not args.skip_waveforms:

        for sim_root_name, bb in args.bb_list:
            if args.obs is not None:
                cmd = f"python {args.gmsim_env}/visualization/waveform/waveforms.py --waveforms {args.obs/'Obs_Acc'} Obs --waveforms {bb} Sim -t {args.time} --acc --no-amp-normalize --stations {args.station_list_str} --out {args.outdir}/waveforms_acc_{sim_root_name}" 
                out,err=exe(cmd)
                print(out)
                print(err)


                cmd = f"python {args.gmsim_env}/visualization/waveform/waveforms.py --waveforms {args.obs/'Obs_Vel'} Obs --waveforms {bb} Sim -t {args.time} --no-amp-normalize --stations {args.station_list_str} --out {args.outdir}/waveforms_vel_{sim_root_name}" 
                out,err=exe(cmd)
                print(out)
                print(err)
            else: # no observation to compare with
                cmd = f"python {args.gmsim_env}/visualization/waveform/waveforms.py --waveforms {bb} Sim -t {args.time} --acc --no-amp-normalize --stations {args.station_list_str} --out {args.outdir}/waveforms_acc_{sim_root_name}"
                out,err=exe(cmd)
                print(out)
                print(err)


                cmd = f"python {args.gmsim_env}/visualization/waveform/waveforms.py --waveforms {bb} Sim -t {args.time} --no-amp-normalize --stations {args.station_list_str} --out {args.outdir}/waveforms_vel_{sim_root_name}"
                out,err=exe(cmd)
                print(out)
                print(err)


    # psa_comparisons
    if not args.skip_psa_comparisons:
        for sim_root_name, im in args.imcsv_list:
            if args.obs is not None:
                obs_ims = (Path(args.obs)/'Obs_IM').glob("*.csv")
                obs_ims = [str(x) for x in obs_ims]
                print(obs_ims)
                obs_im = obs_ims[0]
                cmd = f"python {args.gmsim_env}/visualization/im/psa_comparisons.py --run-name {sim_root_name} --stations {args.station_list_str} --imcsv {im} Sim --imcsv {obs_im} Obs -d {args.outdir}/psa_comparisons_{sim_root_name}"
                out,err=exe(cmd)
                print(out)
                print(err)


            else: # no observation to compare with
                cmd = f"python {args.gmsim_env}/visualization/im/psa_comparisons.py --run-name {sim_root_name} --stations {args.station_list_str} --imcsv {im} Sim -d {args.outdir}/psa_comparisons_{sim_root_name}"
                out,err=exe(cmd)
                print(out)
                print(err)


    # psa_bias
    if not args.skip_psa_bias:
        for sim_root_name, im in args.imcsv_list:
            if args.obs is not None:
                obs_ims = (Path(args.obs)/'Obs_IM').glob("*.csv")
                obs_ims = [str(x) for x in obs_ims]
                print(obs_ims)
                obs_im = obs_ims[0]
                cmd = f"python {args.gmsim_env}/visualization/im/psa_bias.py --run_name {sim_root_name} --imcsv {im} Sim --imcsv {obs_im} Obs -o {args.outdir}/psa_bias_{sim_root_name}"
                out,err=exe(cmd)
                print(out)
                print(err)


            else: # no observation to compare with
                cmd = f"python {args.gmsim_env}/visualization/im/psa_bias.py --run_name {sim_root_name} --imcsv {im} Sim -o {args.outdir}/psa_bias_{sim_root_name}"
                out,err=exe(cmd)
                print(out)
                print(err)   


    # collect im plots
    if not args.skip_implots:
        for sim_root_name, im in args.implots_list:
            outdir = args.outdir/f"im_plots_{sim_root_name}"
            #outdir.mkdir(parents=True,exist_ok=True)
            if outdir.exists():
                shutil.rmtree(outdir)
            listdir=shutil.copytree(im,outdir)
            print(listdir)
         
