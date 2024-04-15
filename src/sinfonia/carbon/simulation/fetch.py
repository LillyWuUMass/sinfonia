import requests
from yarl import URL

from src.domain.logger import get_default_logger
from .metadata import CARBON_TRACE_FILE_PATH


logger = get_default_logger()


def from_github(zone: str, repo_url: str):
    filename = f"{zone}_2023_hourly.csv"
    url = (URL(repo_url) / filename).with_query({"raw": "true"})
    
    logger.debug(f"Fetching carbon trace at {url}")
    
    resp = requests.get(url)
    resp.raise_for_status()
    with open(CARBON_TRACE_FILE_PATH, "w") as f:
        f.write(resp.text)
