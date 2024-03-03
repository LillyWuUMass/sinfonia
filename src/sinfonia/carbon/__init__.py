from .measures import (
    get_carbon_trace,
    get_average_energy_use_joules,
    )
import src.sinfonia.carbon.replay as replay
import src.sinfonia.carbon.unit_conv as unit_conv


@dataclass(init=True)
class CarbonReport():
    """Contains carbon reporting data."""
    carbon_intensity_gco2_kwh: float
    energy_use_joules: float
    carbon_emission_gco2: float
