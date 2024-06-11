import csv
import os
import time
from pathlib import Path

import rapl

from src.lib.time import TimeUnit


def energy_report(
        path: str | Path, 
        reset_interval_seconds: float = TimeUnit.DAY,
        sample_interval_seconds: float = TimeUnit.SECOND,
):
    """Sample energy in Joules via Intel RAPL.
    
    Args:
        path - str | Path: File location to save energy data
        sample_interval_seconds - float: Number of seconds over which to measure energy use [default: 1]
    """
    f = open(Path(path), 'w', encoding='utf-8')
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'average_joules', 'summation_joules'])
    last_reset_ts = int(time.time())
    
    while True:
        # if over reset interval then re-open file and clear all previous contents
        ts = int(time.time())
        if ts - last_reset_ts > reset_interval_seconds:    
            f.close()
            f = open(Path(path), 'w', encoding='utf-8')
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'average_joules', 'summation_joules'])
            last_reset_ts = ts
        
        # measure system energy use over the specified period
        s1 = rapl.RAPLMonitor.sample()
        time.sleep(sample_interval_seconds)
        s2 = rapl.RAPLMonitor.sample()

        diff = s2 - s1
        
        eu_avg, eu_sum = 0, 0
        for d in diff.domains:
            domain = diff.domains[d]
            eu_avg += diff.average_power(package=domain.name)
            eu_sum += diff.energy(package=domain.name, unit=rapl.JOULES)
        
        writer.writerow([ts, eu_avg, eu_sum])
        f.flush()


