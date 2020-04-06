#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Part of odoo_api_lib
# Copyright 2019-2020 David Todd <dtodd@oceantech.com>
# License: MIT License, refer to `license.md` for more information

"""
    Tests the functionality of the API
"""

import os
import sys
# Explicitly add the library to python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from api import API

class Message:
    """
        Contains the messages that are raised upon failed assertions
    """

    PARTNER_SEARCH = 'Search for partner id 1 did not return id 1'
    GROUP_SEARCH = 'Search for group name "Access Rights" did not return id 2'
    PARTNER_READ = 'Read first partner did not return expected fields or values'
    PARTNER_SEARCH_READ = 'Search for and Read first partner did not return expected values'

if __name__ == '__main__':
    # Create an instance of the ERP
    # Load the configuration from environment
    odoo = API(verify_tls=False)

    # Test search operations
    res = odoo.search('res.partner', [('id', '=', 1)])
    assert res == [1], Message.PARTNER_SEARCH

    # Search for a name
    res = odoo.search('res.groups', [('name', 'ilike', 'Access Rights')])
    assert res == [2], Message.GROUP_SEARCH

    # Read a record
    res = odoo.read('res.partner', [1], {'fields': ['name']})
    assert res == [{'id': 1, 'name': 'OceanTech'}], Message.PARTNER_READ

    # Search and Read
    res = odoo.search_and_read('res.partner', [('id', '=', 1)], {'fields': ['name']})
    assert res == [{'id': 1, 'name': 'OceanTech'}], Message.PARTNER_SEARCH_READ
