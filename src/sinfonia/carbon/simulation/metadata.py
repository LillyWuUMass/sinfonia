from typing import Dict, List

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


CARBON_TRACE_FILE_PATH = Path("trace.csv")


@dataclass(init=True, frozen=True)
class MetaData:
    start_date_unix: int
    end_date_unix: int
    

def get_metadata() -> MetaData:
    h = pd.read_csv(CARBON_TRACE_FILE_PATH)        
    return MetaData(
            start_date_unix=h['timestamp'].min(),
            end_date_unix=h['timestamp'].max(),
        )
