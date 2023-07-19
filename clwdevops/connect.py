import subprocess
from dataclasses import dataclass, field

from omegaconf import DictConfig, OmegaConf


@dataclass
class UploadId:
    uid: str
    pid: str = field(init=False)
    user: str = field(init=False)
    date: str = field(init=False)

    def __post_init__(self):
        self.date = self.uid[15:25]
        self.pid = f"{self.date}/{self.uid}"  # project id: YYYY-MM-dd/uid
        self.user = "client" if "-CC-" in self.uid else "admin"

    def __repr__(self) -> str:
        return self.uid


def load_sops_file(fname: str) -> DictConfig:
    sops = subprocess.run(["sops", "-d", fname], capture_output=True, text=True).stdout
    cfg = OmegaConf.create(sops)
    return cfg
