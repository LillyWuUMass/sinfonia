from dataclasses import dataclass, asdict

from .measures import intel_rapl, obelix
from .unit_conv import watts_to_kwh
from .simulation.measures import get_average_carbon_intensity_gco2_kwh
from .simulation.metadata import MetaData, get_metadata

from src.domain.logger import get_default_logger


logger = get_default_logger()


@dataclass(init=True)
class CarbonReport():
    """Contains carbon reporting data."""
    carbon_intensity_gco2_kwh: float
    energy_use_watts: float
    carbon_emission_gco2: float
    
    def to_dict(self):
        return asdict(self)
    
    
def from_simulation(
        node_name: str,
        method: str,
        t_sec: int,
        timestamp: int
) -> CarbonReport:
    """Return simulated carbon report given a timestamp.
    
    Carbon report is drawn from predefined carbon trace dataset.
    
    First, the given timestamp is normalized to the range of the historical 
    carbon trace data. Then, the trace with the closest timestamp to the given
    timestamp is returned.
    
    Args:
        method: Either 'obelix' or 'rapl' 
        t_sec: Interval (seconds) to sample energy
        timestamp - int: Timestamp to get carbon trace
    
    Returns:
        CarbonReport: Carbon trace
    """
    m: MetaData = get_metadata()
    incr = timestamp % (m.end_date_unix - m.start_date_unix)
    timestamp = m.start_date_unix + incr
    
    ci = get_average_carbon_intensity_gco2_kwh(timestamp)
    
    eu = 0
    if method == 'rapl':
        eu = intel_rapl.sample_energy_watts()
    elif method == 'obelix':
        eu = obelix.sample_energy_watts(node_name, t_sec)
        
    # eu = sample_energy_watts()
    ce = ci * watts_to_kwh(eu, t_sec)
    
    return CarbonReport(
        carbon_intensity_gco2_kwh=ci,
        energy_use_watts=eu,
        carbon_emission_gco2=ce,
        )
    