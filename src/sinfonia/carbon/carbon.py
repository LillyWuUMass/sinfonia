import time

import pyRAPL


# Monitor energy usage on all devices (PKG, DRAM) over all sockets
pyRAPL.setup()


def get_instant_energy_use_joules() -> float:
    """Get instantaneous system energy use in Joules via Intel RAPL."""
    meter = pyRAPL.Measurement('sys')
    
    # Instantaneous energy use is measured over a 1-second interval
    meter.begin()
    time.sleep(1)
    meter.end()

    all_pkg = sum(meter.result.pkg)
    all_dram = sum(meter.result.dram)

    # Raw results are in micro-joules
    # Need to convert to joules    
    return (all_pkg + all_dram) / 1e6
