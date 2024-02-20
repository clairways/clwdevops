import subprocess
from omegaconf import DictConfig, OmegaConf


def load_sops_file(fname: str) -> DictConfig:
    sops = subprocess.run(["sops", "-d", fname], capture_output=True, text=True).stdout
    cfg = OmegaConf.create(sops)
    return cfg
