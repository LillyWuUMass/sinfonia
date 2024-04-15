#
# Sinfonia
#
# deploy helm charts to a cloudlet kubernetes cluster for edge-native applications
#
# Copyright (c) 2021-2022 Carnegie Mellon University
#
# SPDX-License-Identifier: MIT
#
import time
from concurrent.futures import CancelledError

from connexion import NoContent
from connexion.exceptions import ProblemException
from flask import current_app, request
from flask.views import MethodView
from pydantic import BaseModel, validator

from src.domain.logger import get_default_logger
from src.sinfonia.carbon import report as carbon_report


class CarbonGet(BaseModel):
    tspad: int = 0
    carbon_trace_timestamp: int = 0
    
    @validator('tspad', 'carbon_trace_timestamp')
    def _check_non_negative(cls, v):
        if v < 0:
            raise ValueError('tspad must be non-negative')
        return v


class CarbonView(MethodView):
    def search(self):
        try:
            req = CarbonGet(**request.args)
        except ValueError as e:
            raise ProblemException(400, "Error", f"Failed to parse request {e!r}")
        
        if 'CARBON_TRACE_TIMESTAMP' not in current_app.config:
            return ProblemException(400, f"carbon trace timestamp not yet recorded")
        
        return carbon_report.from_simulation(current_app.config['CARBON_TRACE_TIMESTAMP'])


class CarbonTraceTimestampView(MethodView):
    def post(self):
        try:
            req = CarbonGet(**request.args)
        except ValueError as e:
            raise ProblemException(400, "Error", f"Failed to parse request {e!r}")
        
        current_app.config['CARBON_TRACE_TIMESTAMP'] = req.carbon_trace_timestamp
        return NoContent, 200


class LivezView(MethodView):
    def search(self):
        return NoContent, 200
    
    
class ReadyzView(MethodView):
    def search(self):
        return NoContent, 200
    
    
class ResuView(MethodView):
    """Resource Utilization"""
    def search(self):
        return current_app.config['K8S_CLUSTER'].get_resources()


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
