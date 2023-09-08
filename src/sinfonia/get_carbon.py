'''
Query real-time carbon metrics of a given coordinator (longitue and latitue).
'''

import json
import logging
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
from attr import define, field

# Configure logging
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants: configure fine and supported providers
CONFIG_PATH_RELATIVE_PATH = "config/carbon_providers.json" # Credentials of carbon providers
CARBON_PROVIDERS = ["WattTime", "ElectricityMap"] # Only these two providers are supported

# Define the CarbonMetrics class using attr
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
    def load_config(provider:str) -> [list, dict, dict]:
        """
        Load the carbon types and providers' credentials from a configuration file
        Return: 
            metric_types: list of metric types
            credential: a dict of the credentials for accessing the APIs
            urls: urls of carbon metrics of the provider
        """
        try:
            with open(CONFIG_PATH_RELATIVE_PATH, "r", encoding="utf-8") as file:
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
    def url_query(url:str, headers:dict, params:dict) -> dict:
        """Query a URL with headers and parameters."""
        try:
            response = requests.get(url, params=params, headers=headers, timeout=3)
            response.raise_for_status()
            assert response.status_code == 200
            return response.json()
        except (RequestException, AssertionError, ValueError):
            logging.exception(f"Failed to query URL: {url}")
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
            logging.exception("Failed to get token from WattTime")
            return None

    def from_watttime(self, metric_types:list, credential:dict, urls:dict) -> dict[str, float]:
        """
        Get carbon metrics from WattTime using coordinates.
        Note: 
        1) The API rate limit is 3000 req/5min and 10 req/second.
        2) Access token will expire after 30 minutes
        """
        login_url = urls.get("login")
        token = self.get_watttime_token(login_url, credential)

        if token is None:
            logging.exception("WattTime API token is required")
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
                metrics[metric_type] = float(result.get("moer", None))

        return metrics

    def from_electricitymap(self, metric_types:list, credential:dict, urls:dict) -> dict[str, float]:
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

    def get_carbon_metrics(self) -> dict[str, float]:
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

