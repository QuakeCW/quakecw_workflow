import argparse
from pathlib import Path
import yaml

def load_args():
    parser= argparse.ArgumentParser()
    parser.add_argument(
        "yaml_file",type=str, help="install yaml file"
    )

    args = parser.parse_args()
    assert(Path(args.yaml_file).exists)
    with open(Path(args.yaml_file),'r') as file:
        args.params=yaml.safe_load(file)


    return args
