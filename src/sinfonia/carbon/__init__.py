from dataclasses import dataclass, asdict

from .measures import (
    get_average_energy_use_joules
)


@dataclass(init=True)
class CarbonReport():
    """Contains carbon reporting data."""
    carbon_intensity_gco2_kwh: float
    energy_use_joules: float
    carbon_emission_gco2: float
    
    def to_dict(self):
        return asdict(self)
