from .carbon import (
    CarbonReport,
    get_average_energy_use_joules,
    )
from .carbon.replay import get_average_carbon_intensity_gco2_kwh
from .carbon.unit_conv import joules_to_kwh


def get_carbon_report(zone: str, timestamp: int) -> CarbonReport:
    """Return system carbon report given zone and timestamp."""
    ci = get_average_carbon_intensity_gco2_kwh(zone, timestamp)
    eu = get_average_energy_use_joules()
    ce = ci * joules_to_kwh(eu)
    
    return CarbonReport(
        carbon_intensity_gco2_kwh=ci,
        energy_use_joules=eu,
        carbon_emission_gco2=ce,
        )
    