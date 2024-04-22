def joules_to_kwh(w: float, t_sec: float = 1) -> float:
    """Convert energy use in joules to kWh
    
    Args:
        joules - float: Energy use in joules
        t_sec - float: Duration of work in seconds [default: 1]
    Returns:
        float: Energy use in kilowatt-hours
    """
    kilojoules = w / 1000.0
    hours = 1 / 3600.0
    return kilojoules * hours
