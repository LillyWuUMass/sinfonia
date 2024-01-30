import requests


def is_json_response(resp: requests.Response) -> bool:
    """Check if response is of JSON type. 
    
    Args:
        resp -- requests.Response: Response object
        
    Return:
        bool
    """
    resp.headers.get('content-type') == 'application/json' 
    