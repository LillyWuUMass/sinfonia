import uuid


def is_valid_uuid(s):
    """Check if string is a valid UUID."""
    try:
        # Attempt to convert the string to a UUID
        uuid_obj = uuid.UUID(s)
        return str(uuid_obj) == s  # Ensure the string representation is the same as the input
    except ValueError:
        return False
    