from typing import Dict, List

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(init=True, frozen=True)
class MetaData:
    start_date_unix: int
    end_date_unix: int


DATA_PATH = Path("src/sinfonia/carbon/trace/data")

# Automatically generated fields
_SUPPORTED_ZONES: List[str] = []
_METADATA: Dict[str, MetaData] = {}


def _prepare_metadata():
    global _SUPPORTED_ZONES, _METADATA

    for p in DATA_PATH.glob("*.csv"):
        zone = p.stem
        _SUPPORTED_ZONES.append(zone)
        h = pd.read_csv(p)
        _METADATA[zone] = MetaData(
            start_date_unix=h['timestamp'].min(),
            end_date_unix=h['timestamp'].max(),
        )


_prepare_metadata()


def is_supported_zone(zone: str) -> bool:
    return zone in _SUPPORTED_ZONES


def get_metadata(zone: str) -> MetaData:
    if not is_supported_zone(zone):
        raise ValueError(f"Zone {zone} is not supported")
    return _METADATA[zone]
