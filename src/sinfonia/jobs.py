#
# Sinfonia
#
# run periodic tasks
#
# Copyright (c) 2022 Carnegie Mellon University
#
# SPDX-License-Identifier: MIT
#

from typing import Dict

import rapl
import pendulum
import requests
from flask_apscheduler import APScheduler
from requests.exceptions import RequestException
from yarl import URL
from time import time
from datetime import datetime, timedelta

from .cloudlets import Cloudlet

from src.lib.time.unit import TimeUnit

from src.domain.logger import get_default_logger

from .carbon import report as carbon_report
from .carbon.measures import intel_rapl as carbon_measures
from src.sinfonia.carbon.unit_conv import joules_to_kilowatt_hours


logger = get_default_logger()
scheduler = APScheduler()


def expire_cloudlets():
    cloudlets = scheduler.app.config["cloudlets"]

    expiration = pendulum.now().subtract(seconds=scheduler.app.config["CLOUDLET_EXPIRY_SECONDS"])

    for cloudlet in list(cloudlets.values()):
        if cloudlet.last_update is not None and cloudlet.last_update < expiration:
            logger.info(f"Removing stale cloudlet at {cloudlet.endpoint}")
            cloudlets.pop(cloudlet.uuid, None)


def start_expire_cloudlets_job():
    scheduler.add_job(
        func=expire_cloudlets,
        trigger="interval",
        seconds=60,
        max_instances=1,
        coalesce=True,
        id="expire_cloudlets",
        replace_existing=True,
    )


def expire_deployments():
    cluster = scheduler.app.config["K8S_CLUSTER"]
    with scheduler.app.app_context():
        cluster.expire_inactive_deployments()


def start_expire_deployments_job():
    scheduler.add_job(
        func=expire_deployments,
        trigger="interval",
        seconds=60,
        max_instances=1,
        coalesce=True,
        id="expire_deployments",
        replace_existing=True,
    )


def report_to_tier1_endpoints():
    config = scheduler.app.config

    tier2_uuid = config["UUID"]
    tier2_endpoint = URL(config["TIER2_URL"]) / "api/v1/deploy"

    cluster = config["K8S_CLUSTER"]
    resources: Dict = cluster.get_resources()
    
    # Inject carbon metrics
    # carbon_report = get_carbon_report(tier2_zone, int(time()))
    if 'CARBON_TRACE_TIMESTAMP' in config:
        r = carbon_report.from_simulation(config["CARBON_TRACE_TIMESTAMP"])
    
        if not 'rapl_energy_sample' in config:
            config['rapl_energy_sample'] = rapl.RAPLMonitor.sample()
            
        r.energy_use_joules = carbon_measures.get_average_energy_between_samples(config['rapl_energy_sample'], rapl.RAPLMonitor.sample())
        r.carbon_emission_gco2 = r.carbon_intensity_gco2_kwh * joules_to_kilowatt_hours(r.energy_use_joules)
        
        resources.update(r.to_dict())
    
    # Inject location data
    locations = [scheduler.app.config["TIER2_GEOLOCATION"].coordinate]

    logger.debug("Reporting %s", str(resources))

    for tier1_url in config["TIER1_URLS"]:
        tier1_endpoint = URL(tier1_url) / "api/v1/cloudlets/"
        try:
            requests.post(
                str(tier1_endpoint),
                json={
                    "uuid": str(tier2_uuid),
                    "endpoint": str(tier2_endpoint),
                    "resources": resources,
                    "locations": locations,
                    },
                )
        except RequestException:
            logger.warn(f"Failed to report to {tier1_endpoint}")


def start_reporting_job():
    config = scheduler.app.config
    if not config["TIER1_URLS"] or config["TIER2_URL"] is None:
        return

    logger.info("Reporting cloudlet status to Tier1 endpoints")
    scheduler.add_job(
        func=report_to_tier1_endpoints,
        trigger="interval",
        seconds=15,
        max_instances=1,
        coalesce=True,
        id="report_to_tier1",
        replace_existing=True,
    )
    

def broadcast_carbon_trace_timestamp_to_tier2s():
    config = scheduler.app.config

    cloudlets = list(config["cloudlets"].values())
    
    curr_timestamp = config["CARBON_TRACE_TIMESTAMP"]
    for cloudlet in cloudlets:
        logger.debug(f"Setting carbon trace timestamp {curr_timestamp} on {cloudlet.name}")
        cloudlet.set_carbon_trace_timestamp(curr_timestamp)
        
    new_timestamp = curr_timestamp + 300
    config["CARBON_TRACE_TIMESTAMP"] = new_timestamp
    # TODO
    assert scheduler.app.config["CARBON_TRACE_TIMESTAMP"] == new_timestamp

    
def start_broadcasting_job():
    config = scheduler.app.config
    if not config["CARBON_TRACE_TIMESTAMP"]:
        return
    
    logger.info("Broadcasting latest carbontrace_start to all the Tier2s")
    scheduler.add_job(
        func=broadcast_carbon_trace_timestamp_to_tier2s,
        trigger="interval",
        seconds=90,
        max_instances=1,
        coalesce=True,
        id="broadcast_carbon_trace_timestamp_to_tier2s",
        replace_existing=True,
    )
