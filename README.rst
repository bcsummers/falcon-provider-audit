=====================
falcon-provider-audit
=====================

|coverage| |code-style| |pre-commit|

A falcon middleware audit provider.

------------
Installation
------------

Install the extension via pip.

.. code:: bash

    > pip install falcon-provider-audit

--------
Overview
--------

This package provides a middleware audit component for the Falcon Web Framework (https://falcon.readthedocs.io/en/stable/index.html). The audit component supports multiple providers so that audit events can be sent to syslog/file logger, database, and/or other.  The falcon-provider-audit package comes with a rotating logging provider and syslog provider, but it also supports custom providers for writing data in other locations (e.g. Postgres, Mysql, etc). When using multiple providers there are some caveats to customizing audit providers. Each provider can have its own audit control which allows for different data sets in the audit event for each provider.  When configuring ``audit_control`` in a resource the settings will be applied to all providers unless there is a nested ``audit_control`` with the key of the provider name (see examples below).

.. NOTE:: The built-in rotating logging and syslog providers convert the audit data to a comma separated string.

This middleware component tries to provide flexibility in what data is added to the event while at the same time not being overly complicated in code. Values from Falcon's **req**, **resource**, and **resp** objects are easy to add to an audit event. Support for nested value and dict attributes are also supported, but only at a single level deep. No path expression like what jmespath or jq support are provided in the current version.

.. IMPORTANT:: Due to the "simple" path expression (e.g., "dict.field" or "list.0") in this component a single "." in supported in any field name. For example if you wanted to add the response header content_type you would add 'headers.content_type' to the resp_fields dict.

--------
Requires
--------
* Falcon - https://pypi.org/project/falcon/

-------------
Audit Control
-------------

The audit control dict uses the key as the label for the audit field.  For the two logger provider the data is logged as a key/value pair in the log (e.g., request_access_route="127.0.0.1", request_path="/users").

.. code:: javascript

    audit_control = {
        'enabled': True,
        'req_fields': {
            'request_access_route': 'access_route',
            'request_forwarded_host': 'forwarded_host',
            'request_host': 'host',
            'request_method': 'method',
            'request_path': 'path',
            'request_port': 'port',
            'request_query_string': 'query_string',
            'request_referer': 'referer',
            'request_remote_addr': 'remote_addr',
            'request_scheme': 'scheme',
            'request_user_agent': 'user_agent',
        },
        'resp_fields': {
            'response_content_length': 'headers.content-length',
            'response_content_type': 'headers.content-type',
            'response_x_cache': 'headers.x-cache',
            'response_status': 'status',
        },
        'resource_fields': {'user_id': 'user_id'},
    }

---------------
Syslog Provider
---------------

The example below is a basic audit middleware using the syslog provider. This example provides common settings for audit control.

.. code:: python

    import falcon

    from falcon_provider_audit.middleware import AuditMiddleware
    from falcon_provider_audit.utils import SyslogAuditProvider


    class AuditMiddleWareResource(object):
        """Example resource to test Audit Middleware."""

        def on_get(self, req, resp):
            """Support GET method."""
            key = req.get_param('key')
            resp.body = 'Audit Captured'


    # Configure Providers
    audit_control = {
        'enabled': True,
        'req_fields': {
            'request_access_route': 'access_route',
            'request_forwarded_host': 'forwarded_host',
            'request_host': 'host',
            'request_method': 'method',
            'request_path': 'path',
            'request_port': 'port',
            'request_query_string': 'query_string',
            'request_referer': 'referer',
            'request_remote_addr': 'remote_addr',
            'request_scheme': 'scheme',
            'request_user_agent': 'user_agent',
        },
        'resp_fields': {
            'response_content_length': 'headers.content-length',
            'response_content_type': 'headers.content-type',
            'response_x_cache': 'headers.x-cache',
            'response_status': 'status',
        },
        'resource_fields': {'user_id': 'user_id'},
    }
    providers = [
        SyslogAuditProvider(
            audit_control=audit_control, host='127.0.0.1', port=5140, socktype='UDP'
        )
    ]
    app = falcon.API(middleware=[AuditMiddleware(providers=providers)])
    app.add_route('/middleware', AuditMiddleWareResource())

Syslog TCP Providers
--------------------

To use the syslog provider to send message over TCP.

.. code:: python

    provider = [
        SyslogAuditProvider(
            audit_control=audit_control, host='127.0.0.1', port=5140, socktype='TCP'
        )
    ]

Syslog UDP Providers
--------------------

To use the syslog provider to send message over UDP.

.. code:: python

    providers = [
        SyslogAuditProvider(
            audit_control=audit_control, host='127.0.0.1', port=5140, socktype='UDP'
        )
    ]

------------------------
Rotating Logger Provider
------------------------

The example below is a basic audit middleware using the rotating logger provider. This example provides common settings for audit control.

.. code:: python

    import falcon

    from falcon_provider_audit.middleware import AuditMiddleware
    from falcon_provider_audit.utils import RotatingLoggerAuditProvider


    class AuditMiddleWareResource(object):
        """Example resource to test Audit Middleware."""

        def on_get(self, req, resp):
            """Support GET method."""
            key = req.get_param('key')
            resp.body = 'Audit Captured'


    # Configure Providers
    audit_control = {
        'enabled': True,
        'req_fields': {
            'request_access_route': 'access_route',
            'request_forwarded_host': 'forwarded_host',
            'request_host': 'host',
            'request_method': 'method',
            'request_path': 'path',
            'request_port': 'port',
            'request_query_string': 'query_string',
            'request_referer': 'referer',
            'request_remote_addr': 'remote_addr',
            'request_scheme': 'scheme',
            'request_user_agent': 'user_agent',
        },
        'resp_fields': {
            'response_content_length': 'headers.content-length',
            'response_content_type': 'headers.content-type',
            'response_x_cache': 'headers.x-cache',
            'response_status': 'status',
        },
        'resource_fields': {'user_id': 'user_id'},
    }
    providers = [
        RotatingLoggerAuditProvider(
            audit_control=audit_control,
            backup_count=5,
            directory=logs,
            filename=audit.log,
            max_bytes=10485760,
        )
    ]
    app = falcon.API(middleware=[AuditMiddleware(providers=providers)])
    app.add_route('/middleware', AuditMiddleWareResource())

-----------
Development
-----------

Installation
------------

After cloning the repository, all development requirements can be installed via pip. For linting and code consistency the pre-commit hooks should be installed.

.. code:: bash

    > pip install falcon-provider-audit[dev]
    > pre-commit install

Testing
-------

.. code:: bash

    > pytest --cov=falcon_provider_audit --cov-report=term-missing tests/

.. |coverage| image:: https://codecov.io/gh/bcsummers/falcon-provider-audit/branch/master/graph/badge.svg?token=prpmecioDm
    :target: https://codecov.io/gh/bcsummers/falcon-provider-audit

.. |code-style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/python/black

.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
