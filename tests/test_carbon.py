from src.sinfonia.carbon.simulation.fetch import fetch_from_github


TRACE_GITHUB_REPO_URL = "https://github.com/k2nt/k2nt.github.io/blob/main/projects/sinfonia/carbon_traces"
TIER2_ZONE = "US-SW-AZPS"

fetch_from_github(TIER2_ZONE, TRACE_GITHUB_REPO_URL)
