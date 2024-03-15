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

import pendulum
import requests
from flask_apscheduler import APScheduler
from requests.exceptions import RequestException
from yarl import URL
from time import time
from datetime import datetime, timedelta

from src.lib.time.unit import TimeUnit

from src.domain.logger import get_default_logger

from src.sinfonia.carbon import CarbonReport
from src.sinfonia.carbon.trace import get_carbon_report


logger = get_default_logger()
scheduler = APScheduler()


def expire_cloudlets():
    cloudlets = scheduler.app.config["cloudlets"]

    expiration = pendulum.now().subtract(seconds=scheduler.app.config["CLOUDLET_EXPIRY_SECONDS"])

    for cloudlet in list(cloudlets.values()):
        if cloudlet.last_update is not None and cloudlet.last_update < expiration:
            logger.info(f"Removing stale {cloudlet}")
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
    tier2_zone = config["TIER2_ZONE"]

    cluster = config["K8S_CLUSTER"]
    resources: Dict = cluster.get_resources()
    
    # Inject carbon metrics
    carbon_report = get_carbon_report(tier2_zone, int(time()))
    resources.update(carbon_report.to_dict())

    logger.info("Reporting %s", str(resources))

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
