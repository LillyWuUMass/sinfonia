#
# Sinfonia
#
# run periodic tasks
#
# Copyright (c) 2022 Carnegie Mellon University
#
# SPDX-License-Identifier: MIT
#

import logging

import pendulum
import requests
from flask_apscheduler import APScheduler
from requests.exceptions import RequestException
from yarl import URL
from time import time
from datetime import datetime, timedelta

from .get_carbon import CarbonMetrics

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = APScheduler()


def expire_cloudlets():
    cloudlets = scheduler.app.config["cloudlets"]

    expiration = pendulum.now().subtract(minutes=5)

    for cloudlet in list(cloudlets.values()):
        if cloudlet.last_update is not None and cloudlet.last_update < expiration:
            logging.info(f"Removing stale {cloudlet}")
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
    tier2_location = config["TIER2_GEO_LOCATION"]
    tier2_zone = config["TIER2_ZONE"]

    cluster = config["K8S_CLUSTER"]
    resources = cluster.get_resources()

    # Add carbon metrics to resources
    carbon_obj = CarbonMetrics(latitude=tier2_location.latitude, longitude=tier2_location.longitude, zone=tier2_zone)
    carbon_metrics = carbon_obj.get_carbon_history((datetime.now()-timedelta(days=2*365)).timestamp()) # gCO2/KWH
    # carbon_metrics = carbon_obj.get_carbon_metrics()
    _, energy_consumption = carbon_obj.get_energy_consumption() # energy in KJ
    resources["carbon_intensity"] = carbon_metrics["carbon_intensity"]
    resources["energy_consumption"] = energy_consumption
    resources["carbon_emission"] = carbon_metrics["carbon_intensity"]*energy_consumption/3600 # gCO2

    logging.info("Got %s", str(resources))

    for tier1_url in config["TIER1_URLS"]:
        tier1_endpoint = URL(tier1_url) / "api/v1/cloudlets/"
        try:
            requests.post(
                str(tier1_endpoint),
                json={
                    "uuid": str(tier2_uuid),
                    "endpoint": str(tier2_endpoint),
                    "resources": resources,
                },
            )
        except RequestException:
            logging.warn(f"Failed to report to {tier1_endpoint}")


def start_reporting_job():
    config = scheduler.app.config
    if not config["TIER1_URLS"] or config["TIER2_URL"] is None:
        return

    logging.info("Reporting cloudlet status to Tier1 endpoints")
    scheduler.add_job(
        func=report_to_tier1_endpoints,
        trigger="interval",
        seconds=15,
        max_instances=1,
        coalesce=True,
        id="report_to_tier1",
        replace_existing=True,
    )
