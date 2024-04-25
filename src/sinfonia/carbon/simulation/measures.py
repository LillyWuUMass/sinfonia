from typing import Dict
from bisect import bisect_left

import pandas as pd

from .metadata import CARBON_TRACE_FILE_PATH

from src.domain.logger import get_default_logger

logger = get_default_logger()



def get_carbon_trace(timestamp: int) -> Dict:
    """Return carbon trace given zone and timestamp."""
    h = pd.read_csv(CARBON_TRACE_FILE_PATH)
    i = bisect_left(h['timestamp'], timestamp)
    return h.iloc[i].to_dict()


def get_average_carbon_intensity_gco2_kwh(timestamp: int) -> float:
    return get_carbon_trace(timestamp)["carbon_intensity_gco2_kwh_direct"]
