#
# Sinfonia
#
# deploy helm charts to a cloudlet kubernetes cluster for edge-native applications
#
# Copyright (c) 2021-2022 Carnegie Mellon University
#
# SPDX-License-Identifier: MIT
#
from concurrent.futures import CancelledError

from connexion import NoContent
from connexion.exceptions import ProblemException
from flask import current_app
from flask.views import MethodView

from src.domain.logger import get_default_logger

from src.sinfonia.carbon import CarbonReport
from src.sinfonia.carbon.trace import get_carbon_report

from flask import request


class CarbonView(MethodView):
    def search(self):
        tspad = request.args.get('tspad', 0)
        timestamp = int(time.time()) + tspad
        zone = current_app.config['TIER2_ZONE']
        return get_carbon_report(zone, ts)


class DeployView(MethodView):
    def post(self, uuid, application_key):
        cluster = current_app.config["K8S_CLUSTER"]
        
        deployment = cluster.get(uuid, application_key, create=True)
        try:
            deployment.deploy()
        except (CancelledError, TimeoutError) as e:
            raise ProblemException(400, "Error", f"Failed to deploy {e!r}")
        except Exception as e:
            raise ProblemException(500, "Error", f"Error occured {e!r}")

        logger = get_default_logger()
        logger.debug(f"deployview post {deployment.asdict()}")

        return [deployment.asdict()]

    def get(self, uuid, application_key):
        cluster = current_app.config["K8S_CLUSTER"]
        deployment = cluster.get(uuid, application_key)
        if deployment is None:
            raise ProblemException(
                404, "Not Found", title="Unable to find existing deployment"
            )
        return deployment.asdict()

    def delete(self, uuid, application_key):
        cluster = current_app.config["K8S_CLUSTER"]
        
        deployment = cluster.get(uuid, application_key)
        if deployment is not None:
            try:
                deployment.expire()
            except Exception as e:
                raise ProblemException(500, "Error", f"Error occured {e!r}")
        
        return NoContent, 204
