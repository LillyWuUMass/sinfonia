from dataclasses import dataclass

import subprocess
import yaml


class HelmResource:
    def __init__(self, cpu: float, memory_mi: float):
        self.cpu = cpu
        self.memory_mi = memory_mi


class HelmChart:
    def __init__(self, chart_ref: str):
        self.chart_ref = chart_ref
    
    def get_helm_chart_values(self):
        # Show the default values of the chart
        result = subprocess.run(
            ["helm", "show", "values", str(self.chart_ref)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.stdout.decode('utf-8')

    def get_resource_request(self):
        values_yaml = self.get_helm_chart_values()
        values = yaml.safe_load(values_yaml)        
        req = values["resources"]["requests"]
        return HelmResource(
            cpu=float(req['cpu']),
            memory_mi=float(req['memory'][:-2])
        )
    