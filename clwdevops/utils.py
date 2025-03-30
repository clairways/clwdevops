import re
import subprocess
from datetime import timedelta
from pathlib import Path

from omegaconf import DictConfig, OmegaConf


def load_sops_file(fname: str) -> DictConfig:
    sops = subprocess.run(["sops", "-d", fname], capture_output=True, text=True).stdout
    cfg = OmegaConf.create(sops)
    return cfg


def get_config_dir(cfgfile: str = "config.yml") -> Path:
    return next(
        (p for p in [Path.cwd(), *Path.cwd().parents] if (p / cfgfile).exists()), None
    )


def parse_timedelta(stamp):
    if "day" in stamp:
        m = re.match(
            r"(?P<d>[-\d]+) day[s]*, (?P<h>\d+):"
            r"(?P<m>\d+):(?P<s>\d[\.\d+]*)",
            stamp,
        )
    else:
        m = re.match(
            r"(?P<h>\d+):(?P<m>\d+):"
            r"(?P<s>\d[\.\d+]*)",
            stamp,
        )
    if not m:
        return ""

    time_dict = {key: float(val) for key, val in m.groupdict().items()}
    if "d" in time_dict:
        return timedelta(
            days=time_dict["d"],
            hours=time_dict["h"],
            minutes=time_dict["m"],
            seconds=time_dict["s"],
        )
    else:
        return timedelta(
            hours=time_dict["h"], minutes=time_dict["m"], seconds=time_dict["s"]
        )
