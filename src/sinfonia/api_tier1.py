#
# Sinfonia
#
# proxy requests to a nearby cloudlet
#
# Copyright (c) 2022 Carnegie Mellon University
#
# SPDX-License-Identifier: MIT
#
from typing import Dict, List, Iterable

import os
from uuid import UUID
from itertools import chain, filterfalse, islice, zip_longest

from connexion import NoContent
from connexion.exceptions import ProblemException
from flask import current_app, request
from flask.views import MethodView
import csv
from time import time

from .client_info import ClientInfo
from .cloudlets import Cloudlet
from .deployment_recipe import DeploymentRecipe
from .matchers import tier1_best_match


# don't try to deploy to more than MAX_RESULTS cloudlets at a time
MAX_RESULTS = 3
# Whenever a cloudlet reports to tier1, the carbon metrics are appended to this csv
CLOUDLET_CARBON_HISTORY_CSV = "logs/cloudlets_carbon_history.csv"


class CloudletsView(MethodView):
    def post(self):
        body = request.json
        if not isinstance(body, dict) or "uuid" not in body:
            return "Bad Request, missing UUID", 400

        cloudlet = Cloudlet.new_from_api(body)
        
        # Create 'logs' folder if not exists
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Record cloudlet carbon history
        with open(CLOUDLET_CARBON_HISTORY_CSV, 'a') as file:
            csv_writer = csv.writer(file)
            
            resources = cloudlet.resources
            unix_time = int(time())
            uuid = cloudlet.uuid
            carbon_intensity = resources.get('carbon_intensity', '')
            energy_consumption = resources.get('energy_consumption', '')
            carbon_emission = resources.get('carbon_emission', '')
            
            csv_writer.writerow([
                unix_time, 
                uuid,
                carbon_intensity, 
                energy_consumption, 
                carbon_emission
                ])
            
        cloudlets = current_app.config["cloudlets"]
        cloudlets[cloudlet.uuid] = cloudlet
        
        return NoContent, 204

    def search(self):
        cloudlets: Dict[UUID, Cloudlet] = current_app.config["cloudlets"]
        return [cloudlet.summary() for cloudlet in cloudlets.values()]


class DeployView(MethodView):
    def post(self, uuid, application_key, results=1):
        # set number of returned results between 1 and MAX_RESULTS
        max_results = max(1, min(results, MAX_RESULTS))

        try:
            requested = DeploymentRecipe.from_uuid(uuid)
            client_info = ClientInfo.from_request(application_key)
        except ValueError:
            raise ProblemException(400, "Bad Request", "Incorrectly formatted request")

        matchers = current_app.config["match_functions"]
        available: List[Cloudlet] = list(current_app.config["cloudlets"].values())
        candidates: Iterable[Cloudlet] = islice(
            tier1_best_match(matchers, client_info, requested, available), max_results
        )

        # fire off deployment requests
        requests = [
            cloudlet.deploy_async(requested.uuid, client_info)
            for cloudlet in candidates
        ]

        # gather the results,
        # - interleave results from cloudlets in case any returned more than requested.
        # - recombine into a single list, drop failed results, and limit to max_results.
        results = list(
            islice(
                filterfalse(
                    lambda r: r is None,
                    chain(*zip_longest(*(request.result() for request in requests))),
                ),
                max_results,
            )
        )

        # all requests failed?
        if not results:
            raise ProblemException(500, "Error", "Something went wrong")

        return results

    def get(self, uuid, application_key):
        raise ProblemException(500, "Error", "Not implemented")
    
    def delete(self, uuid, application_key):
        raise ProblemException(500, "Error", "Not implemented")


class RecipeView(MethodView):
    def get(self, uuid):
        try:
            recipe = DeploymentRecipe.from_uuid(uuid)
        except ValueError:
            raise ProblemException(404, "Not Found", "Deployment recipe not found")

        if recipe.restricted:
            raise ProblemException(403, "Not Found", "Deployment recipe not accessible")

        return recipe.asdict()
