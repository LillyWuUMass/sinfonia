from dataclasses import dataclass

# import src.sinfonia.carbon.trace as trace
import src.sinfonia.carbon.unit_conv as unit_conv


@dataclass(init=True)
class CarbonReport():
    """Contains carbon reporting data."""
    carbon_intensity_gco2_kwh: float
    energy_use_joules: float
    carbon_emission_gco2: float
