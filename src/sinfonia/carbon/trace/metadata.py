from typing import Dict

from dataclasses import dataclass
from pathlib import Path


@dataclass(init=True, frozen=True)
class MetaData():
    start_date_unix: int
    end_date_unix: int
    
    
DATA_PATH = Path("src/sinfonia/carbon/trace/data")
    
_SUPPORTED_ZONES = ['CA-ON', 'US-CAL-CISO']
    
_METADATA: Dict[str, MetaData] = {
    'CA-ON': MetaData(start_date_unix=1577836800, end_date_unix=1672527600),
    'US-CAL-CISO': MetaData(start_date_unix=1577836800, end_date_unix=1672527600),
    }


def is_supported_zone(zone: str) -> bool:
    return zone in _SUPPORTED_ZONES


def get_metadata(zone: str) -> MetaData:
    if not is_supported_zone(zone):
        raise ValueError(f"Zone {zone} is not supported. Supported zones are: {_SUPPORTED_ZONES}")
    return _METADATA[zone]
    