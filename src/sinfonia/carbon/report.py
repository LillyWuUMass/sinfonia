from dataclasses import dataclass, asdict

from .measures import intel_rapl, obelix
from .unit_conv import joules_to_kwh
from .simulation.measures import get_average_carbon_intensity_gco2_kwh

from src.domain.logger import get_default_logger


logger = get_default_logger()


@dataclass(init=True)
class CarbonReport:
    """Contains carbon reporting data."""
    carbon_intensity_gco2_kwh: float
    energy_use_joules: float
    carbon_emission_gco2: float
    
    def to_dict(self):
        return asdict(self)
    
    
def from_simulation(
        node_name: str,
        method: str,
        t_sec: int,
        timestamp: int,
        rapl_sample_interval_seconds: int = 1,
) -> CarbonReport:
    """Return simulated carbon report given a timestamp.
    
    Carbon report is drawn from predefined carbon trace dataset.
    
    First, the given timestamp is normalized to the range of the historical 
    carbon trace data. Then, the trace with the closest timestamp to the given
    timestamp is returned.
    
    Args:
        node_name: Name of current machine
        method: Either 'obelix' or 'rapl' 
        t_sec: Interval (seconds) to sample energy
        timestamp - int: Timestamp to get carbon trace
    
    Returns:
        CarbonReport: Carbon trace
    """    
    ci = get_average_carbon_intensity_gco2_kwh(timestamp)
    
    eu = 0
    if method == 'rapl':
        eu = intel_rapl.sample_energy_joules(rapl_sample_interval_seconds)
    elif method == 'obelix':
        eu = obelix.sample_energy_joules(node_name, t_sec)
        
    ce = ci * joules_to_kwh(eu, t_sec)
    
    return CarbonReport(
        carbon_intensity_gco2_kwh=ci,
        energy_use_joules=eu,
        carbon_emission_gco2=ce,
        )
    