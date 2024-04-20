import time

import rapl


def sample_energy_watts(t_sec: float = 1) -> float:
    """Get instantaneous system energy use in Joules via Intel RAPL.
    
    Args:
        period_seconds - float: Number of seconds over which to measure energy use [default: 1]
        
    Returns:
        float: Average system energy use in Joules over the specified period.
    """
    # Measure system energy use over the specified period
    s1 = rapl.RAPLMonitor.sample()
    time.sleep(t_sec)
    s2 = rapl.RAPLMonitor.sample()

    diff = s2 - s1
    
    eu = 0
    for d in diff.domains:
        domain = diff.domains[d]
        eu += diff.average_power(package=domain.name)

    return eu


def sample_energy_between_samples(sample1, sample2):
    diff = sample2 - sample1
    
    eu = 0
    for d in diff.domains:
        domain = diff.domains[d]
        eu += diff.average_power(package=domain.name)

    return eu
