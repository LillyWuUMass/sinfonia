from dataclasses import dataclass, asdict
from enum import IntEnum

from pathlib import Path

from .meter import intel_rapl, obelix
from .unit_conv import joules_to_kwh
from .types import EnergyReportMethodType
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
        method: EnergyReportMethodType | str,
        energy_csv_path: str | Path,
        period_seconds: int,
        timestamp: int,
) -> CarbonReport:
    """Return simulated carbon report given a timestamp.
    
    Carbon report is drawn from predefined carbon trace dataset.
    
    First, the given timestamp is normalized to the range of the historical 
    carbon trace data. Then, the trace with the closest timestamp to the given
    timestamp is returned.
    
    Args:
        method - ReportMethod | str: Specify the mechanism to sample energy
        energy_csv_path: str | Path
        period_seconds: int - Period to sample energy
        timestamp - int: Unix timestamp to get carbon trace
    
    Returns:
        CarbonReport: Carbon trace
    """    
    ci = get_average_carbon_intensity_gco2_kwh(timestamp)
    
    method = EnergyReportMethodType(method)
    match method:
        case EnergyReportMethodType.RAPL:
            eu = intel_rapl.sample_energy_joules(energy_csv_path, period_seconds)
        case EnergyReportMethodType.OBELIX:
            eu = obelix.sample_energy_joules()
        case _:
            logger.warning("energy method not supported")
            eu = 0
        
    ce = ci * joules_to_kwh(eu)
    
    return CarbonReport(
        carbon_intensity_gco2_kwh=ci,
        energy_use_joules=eu,
        carbon_emission_gco2=ce,
        )
    