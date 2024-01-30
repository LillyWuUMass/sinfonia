def is_success_status_code(status_code: int) -> bool:
    return status_code >= 200 and status_code <= 299
    