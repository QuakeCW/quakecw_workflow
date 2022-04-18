from pathlib import Path
import yaml
from qcore.shared import exe
from qcore import qclogging
from shared import load_args

def main():
    logger = qclogging.get_logger()
    args = load_args()
    params = args.params

    sim_root_dir=Path(params["sim_root_dir"])
    script= Path(params['workflow']) / Path("workflow/automation/execution_scripts/query_mgmt_db.py")
    print(script)
    cmd=f"python {script} {sim_root_dir} --config {sim_root_dir/'task_config.yaml'}"
    res=exe(cmd,debug=False)
    print(res[0])

if __name__ == "__main__":
    main()

