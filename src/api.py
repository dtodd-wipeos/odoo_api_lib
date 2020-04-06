#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Part of odoo_api_lib
# Copyright 2019-2020 David Todd <dtodd@oceantech.com>
# License: MIT License, refer to `license.md` for more information

"""
    Contains the API class, which handles communication with Odoo
"""

import os
import ssl
import xmlrpc.client

class InputError(Exception):
    """
        Raises an exception when some input value is not correct.
        Attributes:
            field - The input field where the error was encountered
            message - The explaination of the error and instructions
                for how to fix it
    """

    def __init__(self, field, message, *args, **kwargs):
        self.field = field
        self.message = message
        super(InputError, self).__init__(*args, **kwargs)

class API:
    """
        Contains the methods required to connect to an Odoo XMLRPC instance
        and to perform queries against the database.

        These fields are configured via keyword arguments or the environment:

        `odoo_host` - string, required, the hostname of your odoo instance.
            Include the `http(s)://` at the beginning

        `odoo_database` - string, required, the database your odoo instance interacts with.
            Case sensitive

        `odoo_user` - integer, optional, the database id of the user to connect to the API with.
            Defaults to 1 for `admin`

        `odoo_pass` - string, required, the password of the user to connect to the API with

        `verify_tls` - boolean, optional. When False, an unverified SSL context will be created
            and the server certificate will not be checked. Default is True
    """

    # The types of query that are able to be made to the Odoo instance
    QUERY_TYPES = ['search', 'create', 'read', 'write', 'unlink', 'search_read']

    def __init__(self, **kwargs):
        """
            Pulls variables from environment and init kwargs and verifies consistency
        """

        self.hostname = kwargs.get('odoo_host', os.environ.get('odoo_host', False))
        self.database = kwargs.get('odoo_database', os.environ.get('odoo_database', False))
        self.user_id = kwargs.get('odoo_user', os.environ.get('odoo_user', False))
        self.user_pass = kwargs.get('odoo_pass', os.environ.get('odoo_pass', False))

        self.verify_tls = bool(kwargs.get('verify_tls', os.environ.get('verify_tls', True)))

        if not self.hostname:
            raise InputError(
                'odoo_host',
                'The hostname of your Odoo instance is required '
                'Set this by doing `export odoo_host=\'<your hostname>\'` '
                'and run the script again')

        if not self.database:
            raise InputError(
                'odoo_database',
                'The database name of your Odoo instance is required '
                'Set this by doing `export odoo_database=\'<your database>\'` '
                'and run the script again')

        if not self.user_id:
            print("WARNING: The odoo user id is not set, defaulting to the admin user")
            self.user_id = 1
        else:
            self.user_id = int(self.user_id)

        if not self.user_pass:
            raise InputError(
                'odoo_pass',
                'The password of your Odoo user is required '
                'Set this by doing `export odoo_pass=\'<your password>\'` '
                'and run the script again')

    def _connect(self):
        """
            Connects to the Odoo instance and returns an XMLRPC object

            if `self.verify_tls` is False and the host contains https,
            do not verify the server's certificate (but still create the
            secure connection)
        """

        endpoint = "%s/xmlrpc/2/object" % (self.hostname)
        if "https" in endpoint and not self.verify_tls:
            # Odoo could be using a self-signed cert or a CA that is not trusted by the script
            # pylint: disable=protected-access
            return xmlrpc.client.ServerProxy(endpoint, context=ssl._create_unverified_context())
        return xmlrpc.client.ServerProxy(endpoint)

    def _query(self, query_type, model, query, options=dict):
        """
            Verifies the `query_type` is supported by the API
            and executes the API request on a new XMLRPC instance, returning the result
        """

        if query_type not in self.QUERY_TYPES:
            raise InputError(
                'query_type',
                'Incorrect Type of query. Available types are: %s' % (', '.join(self.QUERY_TYPES)))

        return self._connect().execute_kw(
            self.database, self.user_id, self.user_pass,
            # This is the "table" that will be interacted with, in Odoo notation
            # (eg, `res.partner` for `res_partner` in postgresql)
            model,
            # Alters how Odoo will behave with the `query` and `options` fields
            query_type,
            # query must be a list containing either a list or dict depending on the query_type
            [query],
            # options will always be an optional dict, but the keys and values will change
            # depending on query_type
            options)

    def search(self, model, query=list, options=dict):
        """
            Searches the `model` for `query` with `options`
            Defaults to search all records with no limit.

            `query` is an Odoo domain, for example: `[('id','=',1)]`

            `options` is a dictionary that supports the following keywords:
                `limit` - Integer, doesn't return more than this value
                `offset` - Integer, when used in conjunction with limit,
                    it will paginate the search results

            Returns a list of record database IDs that matched the `query`
        """

        if not query:
            query = list()

        if not options:
            options = {'limit': 0}

        return self._query('search', model, query, options)

    def create(self, model, query):
        """
            Creates one or more records on `model` with the supplied `query`

            `query` is a dictionary of the fields that are to be added, and
            will fail if it is missing any fields with the attribute `required=True`

            `query` has data type constraint requirements:
                `Date`, `DateTime`, `Binary (base64)` fields are all presented as str()
                Relational fields (`one2many`, `many2one`, `many2many`) are defined at
                https://www.odoo.com/documentation/9.0/reference/orm.html#openerp.models.Model.write

            Unlike most other query_types, it does not take any options

            Returns a list of record database IDs that were created
        """

        return self._query('create', model, query)

    def read(self, model, query, options=dict):
        """
            Reads one or more records on `model` with the supplied `query`

            `query` is a list of record database IDs to read

            `options` is a dictionary that supports the following keywords:
                `fields` - A list of specific fields to read from, when unset all fields are read

            Returns a list of dictionaries, where each dictionary is a record with the
            fields that were read
        """

        return self._query('read', model, query, options)

    def update(self, model, query, options=dict):
        """
            Updates one or more records on `model`, selected with `query`

            `query` is a list of record database IDs to update

            `options` is a dictionary that contains the fields to change, and their new values

            Returns a list of record database IDs that were updated
        """

        return self._query('write', model, query, options)

    def delete(self, model, query):
        """
            Deletes one or more records on `model`, selected with `query`

            `query` is a list of record database IDs to delete

            Unlike most other query_types, it does not take any options

            Returns a list of record database IDs that were deleted
        """

        return self._query('unlink', model, query)

    def search_and_read(self, model, query, options=dict):
        """
            Shortcut for `read()` with the result of `search()` being used as the `query`

            `query` is an Odoo domain, for example: `[('id','=',1)]`

            `options` is a dictionary that supports the following keywords:
                `fields` - A list of specific fields to read from, when unset all fields are read.

            Returns a list of dictionaries, where each dictionary is a record with the
            fields that were read
        """

        return self._query('search_read', model, query, options)
