import pandas as pd
import logging
import os
from pathlib import Path, PosixPath
import boto3
from datetime import datetime as dt
from typing import Tuple

log = logging.getLogger(__name__)
s3c = boto3.client("s3")


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


def get_df_with_metadata(filepath: PosixPath) -> Tuple[pd.DataFrame, dict]:
    """Get dataframe with metadata"""
    metadata = get_csv_metadata(filepath)
    df = pd.read_csv(filepath, comment="#")
    return df, metadata


def write_df_to_csv(df: pd.DataFrame, output: PosixPath, metadata: dict = None) -> None:
    """Write dataframe to csv with metadata"""
    if metadata:
        with open(output, "w") as f:
            for key, value in metadata.items():
                f.write(f"#{key},{value}\n")
    df.to_csv(output, index=None, mode="a")
    return


def upload_files(bucket: str, key: str, src: str) -> None:

    if not os.path.exists(src):
        log.error(f"Source file {src} does not exist")
        return

    src = Path(src)
    if src.is_dir():
        for file in src.rglob("*"):
            if file.is_file():
                s3c.upload_file(
                    Filename=str(file), Bucket=bucket, Key=f"{key}/{file.name}"
                )
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


def aggregate_dataframe_by_time(
    df: pd.DataFrame,
    startTime: pd.Timestamp,
    aggFunc=None,
    timeKey: str = "Timestamp",
    period: str = "1H",
) -> pd.DataFrame:

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if df.empty:
        raise ValueError("df cannot be empty")

    if aggFunc is None:
        dfg = df.groupby(pd.Grouper(key=timeKey, freq=period, origin=startTime))
    else:
        dfg = (
            df.groupby(pd.Grouper(key=timeKey, freq=period, origin=startTime))
            .agg(aggFunc)
            .reset_index()
        )

    return dfg


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
