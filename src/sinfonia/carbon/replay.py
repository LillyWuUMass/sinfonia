from typing import Dict

from bisect import bisect_left
from pathlib import Path

import pandas as pd


DATA_PATH = Path("src/sinfonia/data")
_SUPPORTED_ZONES = ["CA-ON", "US-CAL-CISO"]


def _is_supported_zone(zone: str) -> bool:
    return zone in _SUPPORTED_ZONES


def get_carbon_trace(zone: str, timestamp: int) -> Dict:
    """Return carbon trace given zone and timestamp."""
    if not _is_supported_zone(zone):
        raise ValueError(f"Zone {zone} is not supported. Supported zones are: {_SUPPORTED_ZONES}")
    
    h = pd.read_csv(DATA_PATH / f"{zone}.csv")
    i = bisect_left(h['timestamp'], timestamp)
    return h.iloc[i].to_dict()


def get_average_carbon_intensity_gco2_kwh(zone: str, timestamp: int) -> float:
    return get_carbon_trace(zone, timestamp)["carbon_intensity"]
