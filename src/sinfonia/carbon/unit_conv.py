def watts_to_kwh(w: float, t_sec: float = 1) -> float:
    """Convert energy use in Watts to kWh
    
    Args:
        watts - float: Energy use in Watts
        t_sec - float: Duration of work in seconds [default: 1]
    Returns:
        float: Energy use in kilowatt-hours
    """
    kilowatts = w / 1000.0
    hours = t_sec / 3600.0
    return kilowatts * hours
