from dataclasses import dataclass, asdict

from .measures import get_average_energy_use_joules
from .unit_conv import joules_to_kilowatt_hours
from .simulation.measures import get_average_carbon_intensity_gco2_kwh
from .simulation.metadata import MetaData, get_metadata


@dataclass(init=True)
class CarbonReport():
    """Contains carbon reporting data."""
    carbon_intensity_gco2_kwh: float
    energy_use_joules: float
    carbon_emission_gco2: float
    
    def to_dict(self):
        return asdict(self)
    
    
def from_simulation(timestamp: int):
    """Return simulated carbon report given a timestamp.
    
    Carbon report is drawn from predefined carbon trace dataset.
    
    First, the given timestamp is normalized to the range of the historical 
    carbon trace data. Then, the trace with the closest timestamp to the given
    timestamp is returned.
    
    Args:
        timestamp - int: Timestamp to get carbon trace
    
    Returns:
        CarbonReport: Carbon trace
    """
    m: MetaData = get_metadata()
    incr = timestamp % (m.end_date_unix - m.start_date_unix)
    timestamp = m.start_date_unix + incr
    
    ci = get_average_carbon_intensity_gco2_kwh(timestamp)
    eu = get_average_energy_use_joules()
    ce = ci * joules_to_kilowatt_hours(eu)
    
    return CarbonReport(
        carbon_intensity_gco2_kwh=ci,
        energy_use_joules=eu,
        carbon_emission_gco2=ce,
        )
    