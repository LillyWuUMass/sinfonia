from typing import Dict

from dataclasses import dataclass
from pathlib import Path


@dataclass(init=True, frozen=True)
class MetaData():
    start_date_unix: int = 1577836800
    end_date_unix: int = 1672527600
    
    
DATA_PATH = Path("./data")
    
SUPPORTED_ZONE = ['CA-ON', 'US-CAL-CISO']
    
METADATA: Dict = {
    'CA-ON': MetaData(start_date_unix=1577836800, end_date_unix=1672527600),
    'US-CAL-CISO': MetaData(start_date_unix=1577836800, end_date_unix=1672527600),
    }
    