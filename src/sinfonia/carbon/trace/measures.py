from typing import Dict

import time
from bisect import bisect_left
from pathlib import Path

import pandas as pd

from src.sinfonia.carbon import (
    CarbonReport,
    get_average_energy_use_joules,
    )

from src.sinfonia.carbon.unit_conv import joules_to_kilowatt_hours
from .metadata import DATA_PATH, is_supported_zone, get_metadata, MetaData


def get_carbon_trace(zone: str, timestamp: int) -> Dict:
    """Return carbon trace given zone and timestamp."""
    if not is_supported_zone(zone):
        raise ValueError(f"Zone {zone} is not supported. Supported zones are: {_SUPPORTED_ZONES}")
    
    h = pd.read_csv(DATA_PATH / f"{zone}.csv")
    i = bisect_left(h['timestamp'], timestamp)
    return h.iloc[i].to_dict()


def get_average_carbon_intensity_gco2_kwh(zone: str, timestamp: int) -> float:
    return get_carbon_trace(zone, timestamp)["carbon_intensity_avg"]


def get_carbon_report(zone: str, timestamp: int) -> CarbonReport:
    """Return system carbon report given zone and timestamp.
    
    Args:
        zone - str: Zone for which to get carbon report
        timestamp - int: Timestamp for which to get carbon report.
        
    Returns:
        CarbonReport: Carbon report for the specified zone and timestamp.
    """
    # Translate given time to trace reference time
    m = get_metadata(zone)
    incr = timestamp % (m.end_date_unix - m.start_date_unix)
    timestamp = m.start_date_unix + incr
    
    ci = get_average_carbon_intensity_gco2_kwh(zone, timestamp)
    eu = get_average_energy_use_joules()
    ce = ci * joules_to_kilowatt_hours(eu)
    
    return CarbonReport(
        carbon_intensity_gco2_kwh=ci,
        energy_use_joules=eu,
        carbon_emission_gco2=ce,
        )
