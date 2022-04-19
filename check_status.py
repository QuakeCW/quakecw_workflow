from pathlib import Path
import yaml
from qcore.shared import exe
from qcore import qclogging

def load_args():
    parser= argparse.ArgumentParser()
    parser.add_argument(
        "yaml_file",type=str, help="gmsim yaml file"
    )

    args = parser.parse_args()
    assert(Path(args.yaml_file).exists())
    with open(Path(args.yaml_file),'r') as file:
        args.params=yaml.safe_load(file)


    return args

def main():
    logger = qclogging.get_logger()
    args = load_args()
    params = args.params

    sim_root_dir=Path(params["sim_root_dir"])
    script= Path(params['workflow']) / Path("workflow/automation/execution_scripts/query_mgmt_db.py")
    cmd=f"python {script} {sim_root_dir} --config {sim_root_dir/'task_config.yaml'}"
    res=exe(cmd,debug=False)
    print(res[0])

if __name__ == "__main__":
    main()

