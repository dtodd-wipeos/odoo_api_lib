#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Part of odoo_api_lib
# Copyright 2019-2020 David Todd <dtodd@oceantech.com>
# License: MIT License, refer to `license.md` for more information

"""
    Tests the functionality of the API

    To run these tests, you need to have an Odoo instance.
    Edit `run.sh` to point to your Odoo instance

    The class objects at the top of this file define what
    is being tested, which queries and options, its expected
    result, and the messages that are displayed upon failure

    You will probably have to change the `Result.partner_read`
    to point to your actual first contact.
"""

import os
import sys
# Explicitly add the library to python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from api import API

class Model:
    """
        Contains the models that we are testing against
    """

    partner = 'res.partner'
    group = 'res.groups'

class Query:
    """
        Contains the Queries that we are sending to the API
    """

    partner_search = [('id', '=', 1)]
    group_search = [('name', 'ilike', 'Access Rights')]
    partner_read = [1]
    partner_create = {'name': 'test'}

class Options:
    """
        Contains the Options for the Queries that we are sending
    """

    partner_read = {'fields': ['name']}
    partner_update = {'name': 'abc'}

class Result:
    """
        Contains the values that are expected for each of the tests
    """

    partner_search = [1]
    group_search = [2]
    partner_read = [{'id': 1, 'name': 'OceanTech'}]

class Message:
    """
        Contains the messages that are raised upon failed assertions
    """

    partner_search = 'Search for partner id 1 did not return id 1'
    group_search = 'Search for group name "Access Rights" did not return id 2'
    partner_read = 'Read Partner Record did not return expected fields or values'
    partner_search_read = 'Search for and Read first partner did not return expected values'
    partner_create = 'Partner Create did not return a database id'
    partner_update = 'Unable to Update previously created Partner id'
    partner_delete = 'Unable to Delete previously created Partner id'

    success = 'All tests have successfully passed'

if __name__ == '__main__':
    # Create an instance of the ERP
    # Load the configuration from environment
    odoo = API(verify_tls=False)

    # Test search operations
    print('Testing Search by ID - First Partner Record')
    res = odoo.search(Model.partner, Query.partner_search)
    assert res == Result.partner_search, Message.partner_search

    # Search for a name
    print('Testing Search by field - Second Group Record')
    res = odoo.search(Model.group, Query.group_search)
    assert res == Result.group_search, Message.group_search

    # Read a record
    print('Testing Reading first Partner Record')
    res = odoo.read(Model.partner, Query.partner_read, Options.partner_read)
    assert res == Result.partner_read, Message.partner_read

    # Search and Read
    print('Testing Search and Read first Partner Record')
    res = odoo.search_and_read(Model.partner, Query.partner_search, Options.partner_read)
    assert res == Result.partner_read, Message.partner_search_read

    # Create a dummy record
    print('Testing Create Partner Record')
    res = odoo.create(Model.partner, Query.partner_create)
    assert isinstance(res, int), Message.partner_create
    partner_id = res

    # Update a record (the dummy created above will do nicely)
    print('Testing Update Partner Record')
    res = odoo.update(Model.partner, [partner_id], Options.partner_update)
    assert res == True, Message.partner_update

    # Ensure that it actually changed
    print('- Ensuring it was changed')
    res = odoo.read(Model.partner, [partner_id], Options.partner_read)
    assert res[0]['name'] == 'abc', Message.partner_read

    # Delete a record (the dummy created above will do nicely)
    print('Testing Delete Partner Record')
    res = odoo.delete(Model.partner, [partner_id])
    assert res == True, Message.partner_delete

    # Ensure that it actually got deleted
    print('- Ensuring it was deleted')
    res = odoo.read(Model.partner, [partner_id], Options.partner_read)
    assert len(res) == 0, Message.partner_read

    print(Message.success)
    sys.exit(0)
