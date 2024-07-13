import os
import time
import csv
from pathlib import Path

import rapl


RAPL_FOLDER = os.environ.get('RAPL_FOLDER', '')
OBELIX_NODE_NAME = os.environ.get('OBELIX_NODE_NAME', 'obelix')


def sample_energy_joules(t_sec: float = 1) -> float:
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
    
    eu_avg = 0
    eu_sum = 0
    for d in diff.domains:
        domain = diff.domains[d]
        eu_avg += diff.average_power(package=domain.name)
        eu_sum += diff.energy(package=domain.name, unit=rapl.JOULES)

    return eu_avg, eu_sum


filename = f"{OBELIX_NODE_NAME}-rapl.csv"
with open(Path(RAPL_FOLDER) / filename, 'w', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['timestamp', 'average_joules', 'summation_joules'])
    while True:
        timestamp = int(time.time())
        avg, sum = sample_energy_joules(t_sec=1)
        writer.writerow([timestamp, avg, sum])
        file.flush()
        