import csv
import ast
import logging
import os
from pathlib import PosixPath
from datetime import datetime as dt
from typing import Tuple

log = logging.getLogger(__name__)


def get_csv_metadata(input: PosixPath) -> dict:
    """Get metadata for input file"""
    if not input:
        log.error("No input file provided")
        return {}

    if not os.path.exists(input):
        log.error(f"Input file {input} does not exist")
        return {}

    if not isinstance(input, PosixPath):
        raise TypeError("input must be a PosixPath")
    metadata = {}

    with open(input, "r") as f:
        for line in f:
            if not line.startswith("#"):
                break
            key, value = line[1:].split(",")
            metadata[key] = value.strip()

    return metadata


def decomment(csvfile):
    for row in csvfile:
        raw = row.split("#")[0].strip()
        if raw:
            yield raw


def get_csv_with_metadata(filepath: PosixPath) -> Tuple[dict, dict]:
    """Get dataframe with metadata"""
    metadata = get_csv_metadata(filepath)

    with open(filepath, "r") as f:
        reader = csv.DictReader(decomment(f))
        data = [row for row in reader]

    for idx, d in enumerate(data):  # Fix datatypes that get converted to strings
        for key, value in d.items():
            try:
                data[idx][key] = ast.literal_eval(value)
            except:
                pass
    return data, metadata


def write_csv_with_meta(data: dict, output: PosixPath, metadata: dict = None) -> None:
    """Write dataframe to csv with metadata"""
    if metadata:
        with open(output, "w") as f:
            for key, value in metadata.items():
                f.write(f"#{key},{value}\n")

    # df.to_csv(output, index=None, mode="a")
    with open(output, "a") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    return


def convert_filename_to_datetime(filename: PosixPath) -> dt:
    """Convert filename to datetime
    Assumes filename is in format path/to/file/MMDDYY_XX_HHMMSS.ext"""

    if not isinstance(filename, PosixPath):
        raise TypeError("filename must be a PosixPath")

    basename = filename.stem  # Get the filename without the extension
    components = basename.split("_")  # Split the filename into its components

    date = components[0]  # Get the date
    time = components[2]  # Get the time

    try:
        timestamp = dt.strptime(
            f"{date} {time}", "%m%d%y %H%M%S"
        )  # Combine the date and time into a timestamp
    except ValueError:
        log.error(f"Invalid filename format {filename}")
        return

    return timestamp


def timestamps_to_study_times(timestamps: list) -> dict:

    if not isinstance(timestamps, list):
        raise TypeError("timestamps must be a list")

    studyTimeLabels = ["Timestamp", "StudyDay", "Hour", "HourOfDay"]

    studyTime = {k: [] for k in studyTimeLabels}
    studyTime["Timestamp"] = timestamps
    studyTime["StudyDay"] = [i // 24 + 1 for i in range(len(timestamps))]
    studyTime["Hour"] = [i + 1 for i in range(len(timestamps))]
    studyTime["HourOfDay"] = [(x - 1) % 24 + 1 for x in studyTime["Hour"]]

    return studyTime
