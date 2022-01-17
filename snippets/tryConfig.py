import yaml


def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


import pdb; pdb.set_trace()


config = read_yaml("../config.yaml")

