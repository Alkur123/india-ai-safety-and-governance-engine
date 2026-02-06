import yaml

with open("policies/governance.yaml") as f:
    POL=yaml.safe_load(f)["policies"]

def get_policy(cat):
    return POL.get(cat, POL["SAFE"])
