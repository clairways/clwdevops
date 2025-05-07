import re
from dataclasses import dataclass, field
from pathlib import PosixPath
from datetime import datetime as dt
import logging

log = logging.getLogger(__name__)


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

    @classmethod
    def from_path(cls, path: str):
        """Extract upload id from path"""
        sid = re.search(r"(CLW.{31})", path).group(1)
        return cls(sid)


def convert_filename_to_datetime(filename: PosixPath) -> dt:
    """Convert filename to datetime
    Assumes filename is in format path/to/file/MMDDYY_XX_HHMMSS.ext 
    or path/to/file/MMDDYY_XX_HHMMSSff.ext"""

    if not isinstance(filename, PosixPath):
        raise TypeError("filename must be a PosixPath")

    basename = filename.stem  # Get the filename without the extension
    components = basename.split("_")  # Split the filename into its components

    date = components[0]  # Get the date
    time = components[2]  # Get the time

    if len(time) == 8:
        tfmt = "%m%d%y %H%M%S%f"
    else:
        tfmt = "%m%d%y %H%M%S"

    try:
        timestamp = dt.strptime(
            f"{date} {time}", tfmt
        )  # Combine the date and time into a timestamp
    except ValueError:
        log.error(f"Invalid filename format {filename}")
        return

    return timestamp


def timestamps_to_study_times(timestamps: list[dt]) -> dict:

    if not isinstance(timestamps, list):
        raise TypeError("timestamps must be a list")

    studyTimeLabels = ["Timestamp", "StudyDay", "Hour", "HourOfDay"]

    studyTime = {k: [] for k in studyTimeLabels}
    studyTime["Timestamp"] = timestamps
    studyTime["StudyDay"] = [i // 24 + 1 for i in range(len(timestamps))]
    studyTime["Hour"] = [i + 1 for i in range(len(timestamps))]
    studyTime["HourOfDay"] = [(x - 1) % 24 + 1 for x in studyTime["Hour"]]

    return studyTime
