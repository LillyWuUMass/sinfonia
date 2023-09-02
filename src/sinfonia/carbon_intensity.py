'''
Query realtime carbon metrics (carbon intensity, marginal carbon intensity) 
for a given coordinator (longitue and latitue).
The supported providers are: WattTime, ElectricityMap, and Singularity
'''
from attr import define
import requests
from requests.auth import HTTPBasicAuth
import json
import os
from requests.exceptions import RequestException
import logging


logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_PATH_RELATIVE_PATH = "config/carbon_providers.json"
CARBON_METRICS = ["carbon_intensity", "marginal_carbon_intensity"]

WATTTIME_URLS = {
    "carbon_intensity": "",
    "marginal_carbon_intensity": "https://api2.watttime.org/v2/index",
}

ELECTRICITYMAP_URLS = {
    "carbon_intensity": "https://api.electricitymap.org/v3/carbon-intensity/latest",
    "marginal_carbon_intensity": "", # Not supported
}

SINGULARITY_URLS = {
    "carbon_intensity": "https://api.singularity.energy/v2/consumed/carbon-intensity/latest",
    "marginal_carbon_intensity": "https://api.singularity.energy/v2/marginal/carbon-intensity/latest",
}

@define
class CarbonMetrics:
 
    """Retrieve carbon metrics for a given longitude and latitude of cloudlet.
    Inputs:
        longitude: The longitude of the cloudlet
        latitude: The latitude of the cloudlet

    Returns:
        carbon_metrics: realtime carbon intensity and marginal carbon intensity
    """
    longitude: float 
    latitude: float
    carbon_provider: str
    carbon_metrics: dict[str, float]
          
    @carbon_metrics.validator
    def _valid_carbon_metrics(self, _attribute, value):
        for key, value in self.carbon_metrics.iteritems():
            if not 0.0 <= float(value) <= 1500.0: #TODO: The bound need to update
                raise ValueError("carbon metric {} out of bounds".format(key))  
 
    @staticmethod
    def load_credentials(provider:str) -> list:
        """Load the credentials for the given provider from config json file.
        Three providers are supported: WattTime, ElectricityMap, and Singularity.
        """
        credentials = []
        
        absolute_path = os.path.dirname(__file__)
        config_file = os.path.join(absolute_path, CONFIG_PATH_RELATIVE_PATH)
        with open(config_file, 'r') as f:
            data = json.load(f)

        if provider == "WattTime":
            username = data['WattTime']['username']
            password = data['WattTime']['password']
            credentials.append(username)
            credentials.append(password)
            
        elif provider == "ElectricityMap":
            token = data['ElectricityMap']['token']
            credentials.append(token)
            
        elif provider == "Singularity":
            token = data['Singularity']['token']
            credentials.append(token)
        else:
            raise ValueError("provider {} is not supported".format(provider))
        
        return credentials
 
            
    @staticmethod
    def url_query(url:str, headers:dict, params:dict) -> dict|None:
        """Query URL with headers and parameters.
        """ 
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            result = response.json()
            assert result.status_code == 200
            return result
        
        except (RequestException, AssertionError, ValueError):
            logging.exception("Failed to query url: {}".format(url))
            return None

    def _get_region(self) -> str:
        """Get the region based on longitude and latitude.
        This is needed since Singularity only supports Region in its API
        We use WattTime's API to get the region since only it has the API so far.
        """ 
        provider = "WattTime"
        credentials = self.load_credentials(provider)
        token = self._get_watttime_token(credentials)
        region_url = 'https://api2.watttime.org/v2/ba-from-loc'
        headers = {'Authorization': 'Bearer {}'.format(token)}
        params = {"longitude": self.longitude, "latitude": self.latitude}
        
        result = self._url_query(region_url, headers, params)
        region = result['abbrev'] #TODO: Need to check the output and decide the key manually
        
        return region
    
    def _get_watttime_token(self, credentials:list) -> str | None:
        """Get watttime token with credentials (username, password)
        Note that the token expires in 30 minutes
        """
        login_url = 'https://api2.watttime.org/v2/login'
        
        try:
            response = requests.get(login_url, auth=HTTPBasicAuth(credentials[0], credentials[1]))
            response.raise_for_status()
            result = response.json()
            assert result.status_code == 200
            token = result['token']
            return token
        
        except (RequestException, AssertionError, ValueError):
            logging.exception(f"Failed to get token from WattTime")
            return None


    def from_watttime(self) -> dict:
        """Get carbon metrics from WattTime.
        Raise ValueError if when no valid carbon metric is found.
        Note: 
        1) The API rate limit is 3000 req/5min and 10 req/second.
        2) Access token will expire after 30 minutes
        """
        provider = "WattTime"
        credentials = self.load_credentials(provider)
        token = self._get_watttime_token(credentials)
        
        if token is None:
            raise ValueError("WattTime API token is required")
        headers = {'Authorization': 'Bearer {}'.format(token)}
        params = {"longitude": self.longitude, "latitude": self.latitude}
        
        metrics = {}
        for metric_type in CARBON_METRICS:
            url = WATTTIME_URLS[metric_type]
            if url == "":
                logger.warning("WattTime: metric {} not supported".format(metric_type))
                pass

            result = self.url_query(url, headers, params)
            if result is None:
                logging.exception("WattTime: failed to retrieve metric {}".format(metric_type))
                metric = None
            else:
                metric = result['moer']
            metrics[metric_type] = metric
        return metrics
    
    def from_electricitymap(self) -> dict:
        """Get carbon intensity from ElectricityMap using coordinates.
        Raise ValueError if when no valid carbon intensity is found.
        """
        provider = "ElectricityMap"
        token = self.load_credentials(provider)
        
        if token is None:
            raise ValueError("ElectricityMap API token is required")
        headers = {"auth-token": token}
        params = {"longitude": self.longitude, "latitude": self.latitude}
        
        metrics = {}
        for metric_type in CARBON_METRICS:
            url = ELECTRICITYMAP_URLS[metric_type]
            if url == "":
                logger.warning("ElectricityMap: metric {} not supported".format(metric_type))
                pass

            result = self.url_query(url, headers, params)
            if result is None:
                logging.exception("ElectricityMap: failed to retrieve metric {}".format(metric_type))
                metric = None
            else:
                if metric_type == "carbon_intensity":
                    metric = result["carbonIntensity"]
                elif metric_type == "marginal_carbon_intensity":
                    metric = result["marginalCarbonIntensity"]
            metrics[metric_type] = metric 
        return metrics
  
    def from_singularity(self):
        """Get carbon intensity from Singularity.
        Only region but not longitude and latitude is supported
        """        
        provider = "Singularity"
        token = self.load_credentials(provider)
        
        if token is None:
            raise ValueError("Singularity API token is required")
        headers = {"X-Api-Key": token}
        region = self._get_region()
        params = {"region": region, "source": "EIA"}
        
        metrics = {}
        for metric_type in CARBON_METRICS:
            url = SINGULARITY_URLS[metric_type]
            if url == "":
                logger.warning("Singularity: metric {} not supported".format(metric_type))
                pass

            result = self.url_query(url, headers, params)
            if result is None:
                logging.exception("Singularity: failed to retrieve metric {}".format(metric_type))
                metric = None
            else:
                if metric_type == "carbon_intensity":
                    metric = result['data'][0]['data']['consumed_rate_kg_per_mwh']
                elif metric_type == "marginal_carbon_intensity":
                    metric = result['data'][0]['data']['marginal_rate_kg_per_mwh']
            metrics[metric_type] = metric
        return metrics

    def get_carbon_metrics(self):
        """ Retrieve carbon metrics for a given provider """
        
        provider = self.carbon_provider
        if provider == "WattTime":
            self.carbon_metrics = self.from_watttime()
        elif provider == "ElectricityMap":
            self.carbon_metrics = self.from_electricitymap()
        elif provider == "Singularity":
            self.carbon_metrics = self.from_singularity
        else:
            raise ValueError("Provider {} is not supported".format(provider))

                
        