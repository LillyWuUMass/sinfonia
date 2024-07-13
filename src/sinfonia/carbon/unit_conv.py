def joules_to_kwh(w: float) -> float:
    """Convert energy use in joules to kWh
    
    Args:
        joules - float: Energy use in joules
    Returns:
        float: Energy use in kilowatt-hours
    """
    kilojoules = w / 1000.0
    hours = 1 / 3600.0
    return kilojoules * hours
