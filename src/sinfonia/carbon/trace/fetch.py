import requests
from yarl import URL

from .metadata import CARBON_TRACE_FILE_PATH


def fetch_from_github(zone: str, repo_url: str):
    filename = f"{zone}_2023_hourly.csv"
    url = (URL(repo_url) / filename).with_query({"raw": "true"})
    resp = requests.get(url)
    with open(CARBON_TRACE_FILE_PATH, "w") as f:
        f.write(resp.text)
