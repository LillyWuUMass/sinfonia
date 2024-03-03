def joules_to_kilowatt_hours(joules: float) -> float:
    """Convert energy use in Joules to kilowatt-hours.
    
    Args:
        joules - float: Energy use in Joules
        
    Returns:
        float: Energy use in kilowatt-hours
    """
    return joules / 3.6e6
