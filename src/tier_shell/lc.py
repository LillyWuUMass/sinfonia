"""Manages life cycle of a tier shell command.

Interactions with tier services follow the basic life cyle of an API call:
    1. Make HTTP request to service.
    2. Wait/Receive response.
    3. Check for critical error.
    4. Check response against defined HTTP status code. React as necessary.
    5. Print response (if exists).

This module contains life cycle scripts to streamline the implementation of new
commands. As of writing, we assume JSON to be the data transfer medium for all
client-server communications.
"""
from dataclasses import dataclass

import logging

from src.tier_shell.config import AppConfig


@dataclass(init=True)
class App:
    config: AppConfig
    log: logging.Logger
    
    
def request():      
    raise NotImplementedError()
    
    
def get():
    raise NotImplementedError()
    
    
def post():
    raise NotImplementedError()
    
    
def delete():
    raise NotImplementedError()


def update():
    raise NotImplementedError()
    