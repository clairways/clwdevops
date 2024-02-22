from pathlib import PosixPath
import logging
import os
from typing import Tuple
import csv
import ast

log = logging.getLogger(__name__)


def get_csv_metadata(input: PosixPath, comment: str = "#") -> dict:
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
            if not line.startswith(comment):
                break
            key, value = line[1:].split(",")
            metadata[key] = value.strip()

    return metadata


def decomment(csvfile, comment: str = "#"):
    for row in csvfile:
        raw = row.split(comment)[0].strip()
        if raw:
            yield raw


def get_csv_with_metadata(filepath: PosixPath) -> Tuple[dict, dict]:
    """Get dataframe with metadata"""
    metadata = get_csv_metadata(filepath)

    with open(filepath, "r") as f:
        reader = csv.DictReader(decomment(f))
        data = [row for row in reader]
        if not data:
            data = {key: [] for key in reader.fieldnames}
            return data, metadata
    for idx, d in enumerate(data):  # Fix datatypes that get converted to strings
        for key, value in d.items():
            try:
                data[idx][key] = ast.literal_eval(value)
            except:
                pass
    return data, metadata


def write_csv_with_metadata(
    data: dict, output: PosixPath, metadata: dict = None
) -> None:
    """Write dataframe to csv with metadata"""
    """If data is provided from a pandas dataframe, use df.to_dict(orient='records') to convert to a list of dictionaries"""
    if metadata:
        with open(output, "w") as f:
            for key, value in metadata.items():
                f.write(f"#{key},{value}\n")
    with open(output, "a") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    return
