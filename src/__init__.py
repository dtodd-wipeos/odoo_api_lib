#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Part of odoo_api_lib
# Copyright 2019-2020 David Todd <dtodd@oceantech.com>
# License: MIT License, refer to `license.md` for more information

"""
    The purpose for this package is to provide an extensible
    API for interacting with an Odoo ERP instance's XMLRPC REST
    endpoints.

    `api` contains the base class API that provides the public methods
    (and a couple private ones)

    `exceptions` contains various exceptions that this module can raise
"""

from .api import API

__version__ = '1.0.0'
