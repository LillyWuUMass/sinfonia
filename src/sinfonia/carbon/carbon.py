import time

import pyRAPL


# Monitor energy usage on all devices (PKG, DRAM) over all sockets
pyRAPL.setup()


def get_average_energy_use_joules(period_seconds: float = 1) -> float:
    """Get instantaneous system energy use in Joules via Intel RAPL.
    
    Args:
        period_seconds - float: Number of seconds over which to measure energy use [default: 1]
        
    Returns:
        float: Average system energy use in Joules over the specified period.
    """
    meter = pyRAPL.Measurement('sys')
    
    # Instantaneous energy use is measured over a 1-second interval
    meter.begin()
    time.sleep(period_seconds)
    meter.end()

    all_pkg = sum(meter.result.pkg)
    all_dram = sum(meter.result.dram)

    # Raw results are in micro-joules
    # Need to convert to joules    
    return (all_pkg + all_dram) / 1e6
