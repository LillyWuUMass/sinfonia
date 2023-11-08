#
# Sinfonia
#
# Copyright (c) 2022 Carnegie Mellon University
#
# SPDX-License-Identifier: MIT
#
"""Tier1 match functions

Plugin setup, additional functions can be added by external python modules
by defining 'sinfonia_tier1_matchers' setuptools entry points.
"""

from __future__ import annotations

import csv
import logging
import os
import random
import time
from operator import itemgetter
from typing import Callable, Iterator, List, Sequence

from importlib_metadata import EntryPoint, entry_points

from .client_info import ClientInfo
from .cloudlets import Cloudlet
from .deployment_recipe import DeploymentRecipe


logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

CURRENT_PATH = os.path.abspath(__file__)
PROJECT_PATH = os.path.dirname(CURRENT_PATH)
LOG_PATH = f"{PROJECT_PATH}/{logs}"

# Type definition for a Sinfonia Tier1 match function
Tier1MatchFunction = Callable[
    [ClientInfo, DeploymentRecipe, List[Cloudlet]], Iterator[Cloudlet]
]


def get_match_function_plugins() -> dict[str, EntryPoint]:
    """Returns a list of match function plugin entrypoints"""
    return {ep.name: ep for ep in entry_points(group="sinfonia.tier1_matchers")}


def tier1_best_match(
    match_functions: Sequence[Tier1MatchFunction],
    client_info: ClientInfo,
    deployment_recipe: DeploymentRecipe,
    cloudlets: list[Cloudlet],
) -> Iterator[Cloudlet]:
    """Generator which yields cloudlets based on selected matchers."""
    for matcher in match_functions:
        yield from matcher(client_info, deployment_recipe, cloudlets)


# ------------------ Collection of Match functions follows --------------


def match_by_network(
    client_info: ClientInfo,
    _deployment_recipe: DeploymentRecipe,
    cloudlets: list[Cloudlet],
) -> Iterator[Cloudlet]:
    """Yields any cloudlets that claim to be local.
    Also removes cloudlets that explicitly blacklist the client address
    """

    # Used to jump the loop whenever a cloudlet can be removed from the list
    class DropCloudlet(Exception):
        pass

    for cloudlet in cloudlets[:]:
        try:
            for network in cloudlet.rejected_clients:
                if client_info.ipaddress in network:
                    logger.debug("Cloudlet (%s) would reject client", cloudlet.name)
                    raise DropCloudlet

            for network in cloudlet.local_networks:
                if client_info.ipaddress in network:
                    logger.info("network (%s)", cloudlet.name)
                    cloudlets.remove(cloudlet)
                    yield cloudlet

            for network in cloudlet.accepted_clients:
                if client_info.ipaddress not in network:
                    logger.debug("Cloudlet (%s) will not accept client", cloudlet.name)
                    raise DropCloudlet

        except DropCloudlet:
            cloudlets.remove(cloudlet)


def _estimated_rtt(distance_in_km):
    """Estimated RTT based on distance and speed of light
    Only used for logging/debugging.
    """
    speed_of_light = 299792.458
    return 2 * (distance_in_km / speed_of_light)


def match_by_location(
    client_info: ClientInfo,
    _deployment_recipe: DeploymentRecipe,
    cloudlets: list[Cloudlet],
) -> Iterator[Cloudlet]:
    """Yields any geographically close cloudlets"""
    if client_info.location is None:
        return

    by_distance = []

    for cloudlet in cloudlets:
        distance = cloudlet.distance_from(client_info.location)
        if distance is not None:
            by_distance.append((distance, cloudlet))

    if not by_distance:
        return

    by_distance.sort(key=itemgetter(0))
    for distance, cloudlet in by_distance:
        logger.info(
            "distance (%s) %d km, %.3f minRTT",
            cloudlet.name,
            distance,
            _estimated_rtt(distance),
        )
        cloudlets.remove(cloudlet)
        yield cloudlet


def match_random(
    _client_info: ClientInfo,
    _deployment_recipe: DeploymentRecipe,
    cloudlets: list[Cloudlet],
) -> Iterator[Cloudlet]:
    """Shuffle anything that is left and return in randomized order"""
    random.shuffle(cloudlets)
    for cloudlet in cloudlets[:]:
        logger.info("random (%s)", cloudlet.name)
        cloudlets.remove(cloudlet)
        yield cloudlet


def _append_to_csv(path: str, header: List[Any], row: List[Any]):
    """Append a row to a CSV file"""
    # Create logs folder if it does not exist
    os.makedirs(LOG_PATH, exists_ok=True)

    # If CSV file does not exist then create one and append header
    if os.path.exists(path):
        with open(path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.write(header)

    # Check that the given row has the correct number of elements
    if len(header) != len(row):
        raise Exception(f"Row contains incorrect number of elements. Expected {len(header)} found {len(row)}")

    with open(path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.write(row)


CARBON_INTENSITY_LOG_FILE_PATH = f"{LOG_PATH}/carbon_intensity.csv"
CARBON_INTENSITY_CSV_HEADER = ['timestamp', 'names', 'carbon_intensity_gco2_per_kwh']


def match_carbon_intensity(
    _client_info: ClientInfo,
    _deployment_recipe: DeploymentRecipe,
    cloudlets: list[Cloudlet],
) -> Iterator[Cloudlet]:
    """Yields cloudlet recommendations based on lowest carbon intensity level"""

    # Sort cloudlets by lowest carbon intensity level
    sorted(cloudlets, key=lambda c: c.resources['carbon_intensity'])

    # Append decision to persistent log
    # This is for debugging purposes only
    timestamp = int(time.time())
    names = [c.name for c in cloudlets]
    carbon_intensity = [c.resources['carbon_intensity'] for c in cloudlets]
    _append_to_csv(
        path=CARBON_INTENSITY_LOG_FILE_PATH,
        header=CARBON_INTENSITY_CSV_HEADER,
        row=[timestamp, names, carbon_intensity]
    )

    # Yield cloudlets
    for cloudlet in cloudlets:
        logger.info(f"[carbon_intensity] {cloudlet.name} {cloudlet.resources['carbon_intensity']} gCO2/kWh")
        cloudlets.remove(cloudlet)
        yield cloudlet
