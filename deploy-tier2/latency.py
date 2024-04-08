import time
import subprocess

import yaml
import geopy.distance


LIGHT_SPEED_KM_PER_MS = 299.792458
LATENCY_VARIANCE = 0.05
NETWORK_INTERFACES = ['eno1', 'kilo0']


# newport_ri = (41.49008, -71.312796)
# cleveland_oh = (41.499498, -81.695391)
# adelaide = (-34.921230, 138.599503)
# amherst = (42.340382, -72.496819)
# print(geopy.distance.distance(adelaide, amherst).km)


with open("inv.yaml", "r") as f:
    inv = yaml.safe_load(f)
    
    client_data = list(inv["client"]["hosts"].values())[0]
    client_coordinate = (
        client_data["sinfonia_tier2_latitude"],
        client_data["sinfonia_tier2_longitude"],
        )
    print("client", client_coordinate)
    
    # client_cooridate = ("42.340382", "-72.496819")
    
    host_datas = inv["tier2hosts"]["hosts"]
    for host, data in host_datas.items():
        host_coordinate = (
            data["sinfonia_tier2_latitude"],
            data["sinfonia_tier2_longitude"],
            )
        dist_km = geopy.distance.distance(client_coordinate, host_coordinate).km
        
        latency_ms = round(dist_km / LIGHT_SPEED_KM_PER_MS, 1)
        latency_variance_ms = round(latency_ms * LATENCY_VARIANCE, 1)
        
        for itf in NETWORK_INTERFACES:
            cmd = ([
                'sudo',
                'tc',
                'qdisc',
                'add',
                'dev',
                f'{itf}',
                'root', 
                'netem', 
                'delay',
                f'{latency_ms}ms',
                f'{latency_variance_ms}ms'
                ])
            print(cmd)
            subprocess.run(cmd)
            time.sleep(1)
        
        # print(host, dist_km, host_coordinate, latency_ms, latency_variance_ms)
        