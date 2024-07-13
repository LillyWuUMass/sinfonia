import pandas as pd
from pathlib import Path


def sample_energy_joules(
        energy_csv_path: str | Path,
        period_seconds: float = 1,
) -> float:
    """Get instantaneous system energy use in Joules via Intel RAPL.
    
    Args:
        energy_csv_path: str | Path: Path to read energy CSV
        period_seconds - float: Number of seconds over which to measure total energy use [default: 1]
        
    Returns:
        float: Average system energy use in Joules over the specified period.
    """
    df = pd.read_csv(energy_csv_path, on_bad_lines="skip")
    energy_joules_samples = df.tail(period_seconds).iloc[:, -1]
    return energy_joules_samples.sum()
