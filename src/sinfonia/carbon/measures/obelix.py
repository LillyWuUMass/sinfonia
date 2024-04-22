import requests
import json

from yarl import URL


def sample_energy_joules(node_name, t_sec: int = 15) -> float:
    POWER_MONITOR_URL = URL(f"http://192.168.245.31:5050/api/v1/monitor/{node_name}/energy")
    POWER_MONITOR_URL = POWER_MONITOR_URL.with_query({"tsec": t_sec})
    resp = requests.get(POWER_MONITOR_URL)
    resp.raise_for_status()
    data = json.loads(str(resp.json()).replace('\'', '\"'))
    return data['data']['eu']
