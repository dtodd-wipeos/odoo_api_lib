#!/bin/bash
# Part of odoo_api_lib
# Copyright 2019-2020 David Todd <dtodd@oceantech.com>
# License: MIT License, refer to `license.md` for more information

# This script provides the base configuration needed to run the tests
# Testing requires an Odoo instance that has the XMLRPC interface enabled (default)

export odoo_host='<URL of your Odoo instance, including http(s)>'
export odoo_database='<Database of your Odoo instance>'
export odoo_user=1
export odoo_pass='<Password for admin user>'

python3 test.py
