# -*- coding: utf-8 -*-
"""Falcon app used for testing."""
# third-party
import falcon

# first-party
from falcon_provider_audit.middleware import AuditMiddleware
from falcon_provider_audit.utils import RotatingLoggerAuditProvider, SyslogAuditProvider

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


class RotatingLoggerResource1:
    """Memcache middleware testing resource."""

    # pylint: disable=no-self-use
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        key: str = req.get_param('key')
        resp.body = f'Audited - {key}'
        resp.set_header('content-type', 'application/json')

    # pylint: disable=no-self-use
    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support POST method."""
        key: str = req.get_param('key')
        value: str = req.get_param('value')
        resp.body = f'Audited - {key} {value}'
        resp.set_header('content-type', 'application/json')


providers = [RotatingLoggerAuditProvider(audit_control=audit_control, logger_name='ROT1')]

app_rotating_logger_1 = falcon.API(middleware=[AuditMiddleware(providers=providers)])
app_rotating_logger_1.add_route('/middleware', RotatingLoggerResource1())


class RotatingLoggerResource2:
    """Memcache middleware testing resource."""

    # update global audit_controls
    audit_control = {
        'enabled': True,
        'rotating_logger': {
            'enabled': True,
            'req_fields': {'request_access_route': 'access_route.0'},
            'resource_fields': {},
        },
    }

    # pylint: disable=no-self-use
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        key: str = req.get_param('key')
        resp.body = f'Audited - {key}'
        resp.set_header('content-type', 'application/json')

    # pylint: disable=no-self-use
    def on_put(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support PUT method."""
        key: str = req.get_param('key')
        value: str = req.get_param('value')
        resp.body = f'Audited - {key} {value}'
        resp.set_header('content-type', 'application/json')


providers = [RotatingLoggerAuditProvider(audit_control=audit_control, logger_name='ROT2')]

app_rotating_logger_2 = falcon.API(middleware=[AuditMiddleware(providers=providers)])
app_rotating_logger_2.add_route('/middleware', RotatingLoggerResource2())


class DualLoggerResource1:
    """Memcache middleware testing resource."""

    # pylint: disable=no-self-use
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        key = req.get_param('key')
        resp.body = f'Audited - {key}'
        resp.set_header('content-type', 'application/json')

    # pylint: disable=no-self-use
    def on_put(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support PUT method."""
        key = req.get_param('key')
        value = req.get_param('value')
        resp.body = f'Audited - {key} {value}'
        resp.set_header('content-type', 'application/json')


class DualLoggerResource2:
    """Memcache middleware testing resource."""

    # update global audit_controls
    audit_control = {
        'rotating_logger': {
            'enabled': True,
            'req_fields': {'request_access_route': 'access_route.0'},
            'resource_fields': {},
        },
        'syslog': {
            'enabled': False,
            'req_fields': {'request_access_route': 'access_route.0'},
            'resource_fields': {},
        },
    }

    # pylint: disable=no-self-use
    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        key = req.get_param('key')
        resp.body = f'Audited - {key}'
        resp.set_header('content-type', 'application/json')

    # pylint: disable=no-self-use
    def on_put(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support PUT method."""
        key = req.get_param('key')
        value = req.get_param('value')
        resp.body = f'Audited - {key} {value}'
        resp.set_header('content-type', 'application/json')


providers = [
    RotatingLoggerAuditProvider(audit_control=audit_control, logger_name='ROT3'),
    SyslogAuditProvider(audit_control=audit_control, host='0.0.0.0', port=5141, socktype='UDP'),
]

app_dual_logger_1 = falcon.API(middleware=[AuditMiddleware(providers=providers)])
app_dual_logger_1.add_route('/middleware', DualLoggerResource1())
app_dual_logger_1.add_route('/middleware2', DualLoggerResource2())
