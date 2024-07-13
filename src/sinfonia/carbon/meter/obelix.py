import requests
import json

from yarl import URL


def sample_energy_joules(
        node_name: str, 
        period_seconds: int = 15
) -> float:
    raise NotImplementedError()
