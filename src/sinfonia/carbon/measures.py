import time
import rapl
import requests


POWER_MONITOR_SERVICE_ENDPOINT = "http://192.168.245.31:5050/api/v1/monitor/{}/energy"


def get_energy_from_rapl_use_joules(period_seconds: float = 1) -> float:
    """Get instantaneous system energy use in Joules via Intel RAPL.
    
    Args:
        period_seconds - float: Number of seconds over which to measure energy use [default: 1]
        
    Returns:
        float: Average system energy use in Joules over the specified period.
    """
    # Measure system energy use over the specified period
    s1 = rapl.RAPLMonitor.sample()
    time.sleep(period_seconds)
    s2 = rapl.RAPLMonitor.sample()

    diff = s2 - s1
    
    eu = 0
    for d in diff.domains:
        domain = diff.domains[d]
        eu += diff.average_power(package=domain.name)

    return eu


def get_energy_from_obelix_power_monitor(node: str) -> float:
    """
    Calculates total energy consumption of an obelix node in Joules in the past 15 seconds

    Args:
        node: Name of the node (str).

    Returns:
        Total energy consumption in Joules (float), or None if errors occur.
    """

    t_sec = 15

    power_monitor_service_url = POWER_MONITOR_SERVICE_ENDPOINT.format(node)
    params = {"tsec": t_sec}
    # node_power_data = requests.get(power_monitor_service_url, params=params)
    node_power_data = 102.3
    
    print(node_power_data)
    
    return node_power_data
