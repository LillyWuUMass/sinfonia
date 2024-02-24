'''
Query real-time carbon metrics of a given coordinator (longitue and latitue).
'''
from typing import Dict

import json
import requests
from attr import define, field
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

import csv
import rapl
import time
from pathlib import Path

from pydantic import BaseModel

from src.domain.logger import get_default_logger


logger = get_default_logger()


# Carbon replay data
DATA_PATH = Path("src/sinfonia/data")
# Credentials of carbon providers
CONFIG_PATH = "src/sinfonia/config/carbon_providers.json"
# Only these two providers are supported
CARBON_PROVIDERS = ["WattTime", "ElectricityMap"]


class CarbonInfo(BaseModel):
    """Contains carbon reporting information."""
    intensity: float
    energy_consumption: float
    emission: float


@define
class CarbonMetrics:
    """
    Retrieve carbon metrics for a given longitude and latitude of a cloudlet.
    Inputs:
        longitude: the longitude of the cloudlet
        latitude: the latitude of the cloudlet
    """
    latitude: float = field()
    longitude: float = field()
    zone: str = field()

    # Validators for latitude and longitude
    @latitude.validator
    def _valid_latitude(self, _attribute, value):
        if not -90.0 <= value <= 90.0:
            raise ValueError("latitude out of bounds")

    @longitude.validator
    def _valid_longitude(self, _attribute, value):
        if not -180.0 <= value <= 180.0:
            raise ValueError("latitude out of bounds")

    @staticmethod
    def load_config(provider:str) -> [list, Dict, Dict]:
        """
        Load the carbon types and providers' credentials from a configuration file
        Return: 
            metric_types: list of metric types
            credential: a dict of the credentials for accessing the APIs
            urls: urls of carbon metrics of the provider
        """
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
            metric_types = data.get("CarbonMetrics", [])
            carbon_providers = data.get("CarbonProviders", [])
            provider_info = next((p for p in carbon_providers if p["name"] == provider), None)
            if provider_info:
                credential = provider_info.get("credential", {})
                urls = provider_info.get("urls", {})
                for metric_type in metric_types:
                    urls.setdefault(metric_type, None)
                return metric_types, credential, urls

            logger.warning(f"Provider {provider} is not defined in the config file")
            return None, None, None
        except Exception as e:
            logger.exception(f"Error loading config file: {e}")
            return None, None, None

    @staticmethod
    def url_query(url:str, headers:Dict, params:Dict) -> Dict:
        """Query a URL with headers and parameters."""
        try:
            response = requests.get(url, params=params, headers=headers, timeout=3)
            response.raise_for_status()
            assert response.status_code == 200
            return response.json()
        except (RequestException, AssertionError, ValueError):
            logger.exception(f"Failed to query URL: {url}")
            return None

    @staticmethod
    def get_watttime_token(login_url, credential) -> str:
        """
        Get a WattTime token with credentials (username, password)
        Note that the token expires in 30 minutes
        """
        username = credential["username"]
        password = credential["password"]
        try:
            response = requests.get(login_url, auth=HTTPBasicAuth(username, password), timeout=3)
            response.raise_for_status()
            assert response.status_code == 200
            result = response.json()
            return result.get("token", None)
        except (RequestException, AssertionError, ValueError):
            logger.exception("Failed to get token from WattTime")
            return None

    def from_watttime(self, metric_types:list, credential:Dict, urls:Dict) -> Dict[str, float]:
        """
        Get carbon metrics from WattTime using coordinates.
        Note: 
        1) The API rate limit is 3000 req/5min and 10 req/second.
        2) Access token will expire after 30 minutes
        """
        login_url = urls.get("login")
        token = self.get_watttime_token(login_url, credential)

        if token is None:
            logger.exception("WattTime API token is required")
            return None

        headers = {"Authorization": f"Bearer {token}"}
        params = {"latitude": str(self.latitude), "longitude": str(self.longitude)}

        metrics = {}
        for metric_type in metric_types:
            metrics[metric_type] = None
            url = urls.get(metric_type, "")
            if not url:
                logger.warning(f"WattTime: metric {metric_type} not supported")
                continue

            result = self.url_query(url, headers, params)
            if result is None:
                logger.exception(f"WattTime: failed to retrieve metric {metric_type}")
            else:
                logger.info(f"WattTime: result of metric {metric_type}: {result}")
                metrics[metric_type] = float(result.get("moer", 0.0))
                # "moer" is available only for PRO subscriptions.

        return metrics

    def from_electricitymap(self, metric_types:list, credential:Dict, urls:Dict) -> Dict[str, float]:
        """Get carbon intensity from ElectricityMap using coordinates."""
        token = credential.get("token")
        headers = {"auth-token": token}
        params = {"lon": str(self.longitude), "lat": str(self.latitude)}

        metrics = {}
        for metric_type in metric_types:
            metrics[metric_type] = None
            url = urls.get(metric_type, "")
            if not url:
                logger.warning(f"ElectricityMap: metric {metric_type} not supported")
                continue

            result = self.url_query(url, headers, params)
            if result is None:
                logger.exception(f"ElectricityMap: failed to retrieve metric {metric_type}")
            else:
                logger.info(f"ElectricityMap: result of metric {metric_type}: {result}")
                if metric_type == "carbon_intensity":
                    metrics[metric_type] = float(result.get("carbonIntensity", None))
                elif metric_type == "marginal_carbon_intensity":
                    metrics[metric_type] = float(result.get("marginalCarbonIntensity", None))

        return metrics

    def carbon_metrics(self) -> Dict[str, float]:
        """ Retrieve carbon metrics from providers: WattTime, ElectricityMap"""
        carbon_metrics = {}
        wt_metrics = {}
        em_metrics = {}
        for provider in CARBON_PROVIDERS:
            metric_types, credential, urls = self.load_config(provider)
            if not (metric_types and credential and urls):
                logger.warning(f"Configuration is not completed for provider {provider}")
            elif provider == "WattTime":
                wt_metrics = self.from_watttime(metric_types, credential, urls)
                logger.info(f"Carbon metrics from {provider} are: {wt_metrics}")
            elif provider == "ElectricityMap":
                em_metrics = self.from_electricitymap(metric_types, credential, urls)
                logger.info(f"Carbon metrics from {provider} are: {em_metrics}")

        for metric_type in metric_types:
            wt_value = wt_metrics.get(metric_type)
            em_value = em_metrics.get(metric_type)
            carbon_metrics[metric_type] = wt_value if wt_value is not None else em_value

        logger.info(f"Carbon metrics are {carbon_metrics}")
        return carbon_metrics

    def get_energy_consumption(self) -> [float, float]:
        """ Get the average power and energy consumption using rapl"""
        s1 = rapl.RAPLMonitor.sample()
        # Some work that you want to measure.
        time.sleep(1)
        s2 = rapl.RAPLMonitor.sample()

        # Take the difference of the samples
        diff = s2 - s1

        # Compute the power
        total_avg_power = 0
        for d in diff.domains:
            domain = diff.domains[d]
            total_avg_power += diff.average_power(package=domain.name)

        energy_consumption = (total_avg_power) / 1000

        return total_avg_power, energy_consumption

    def carbon_history(self, timestamp: float) -> dict:
        """ Retrieve the carbon intensity of a zone from a past timestamp"""

        ZONES = ["CA-ON", "US-CAL-CISO"]
    
        if self.zone not in ZONES:
            logger.warning(f"Carbon metrics not available for the zone: {self.zone}")
            return None
            
        with open(DATA_PATH / f'{self.zone}.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                if float(row["timestamp"]) <= timestamp and timestamp - float(row["timestamp"]) < 3600:
                    return {"timestamp": timestamp, "carbon_intensity": float(row["carbon_intensity_avg"])}

            logger.warning(f"Carbon metrics not available for the timestamp: {timestamp} in zone: {self.zone}")    
            return None
