import subprocess
from pathlib import Path

from omegaconf import DictConfig, OmegaConf


def load_sops_file(fname: str) -> DictConfig:
    sops = subprocess.run(["sops", "-d", fname], capture_output=True, text=True).stdout
    cfg = OmegaConf.create(sops)
    return cfg


def get_config_dir(cfgfile: str = "config.yml") -> Path:
    return next((p for p in [Path.cwd(), *Path.cwd().parents] if (p / cfgfile).exists()), None)
