"""Falcon app used for testing."""
# third-party
import falcon

# first-party
from falcon_provider_audit.middleware import AuditMiddleware
from falcon_provider_audit.utils import SyslogAuditProvider

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
tcp_providers = [
    SyslogAuditProvider(
        audit_control=audit_control, host='0.0.0.0', logger_name='TCP', port=5141, socktype='TCP'
    )
]
udp_providers = [
    SyslogAuditProvider(
        audit_control=audit_control, host='0.0.0.0', logger_name='UDP', port=5140, socktype='UDP'
    )
]


class TcpSysLogResource1:
    """Audit middleware testing resource."""

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        key = req.get_param('key')
        resp.text = f'Audited - {key}'
        resp.set_header('content-type', 'application/json')

    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support POST method."""
        key = req.get_param('key')
        value = req.get_param('value')
        resp.text = f'Audited - {key} {value}'
        resp.set_header('content-type', 'application/json')


app_tcp_syslog_logger_1 = falcon.App(middleware=[AuditMiddleware(providers=tcp_providers)])
app_tcp_syslog_logger_1.add_route('/middleware', TcpSysLogResource1())


class TcpSysLogResource2:
    """Audit middleware testing resource."""

    # update global audit_controls
    audit_control = {
        'enabled': True,
        'syslog': {
            'enabled': True,
            'req_fields': {'request_access_route': 'access_route.0'},
            'resource_fields': {},
        },
    }

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        key = req.get_param('key')
        resp.text = f'Audited - {key}'
        resp.set_header('content-type', 'application/json')

    def on_put(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support PUT method."""
        key = req.get_param('key')
        value = req.get_param('value')
        resp.text = f'Audited - {key} {value}'
        resp.set_header('content-type', 'application/json')


app_tcp_syslog_logger_2 = falcon.App(middleware=[AuditMiddleware(providers=tcp_providers)])
app_tcp_syslog_logger_2.add_route('/middleware', TcpSysLogResource2())


class UdpSysLogResource1:
    """Audit middleware testing resource."""

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        key = req.get_param('key')
        resp.text = f'Audited - {key}'
        resp.set_header('content-type', 'application/json')

    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support POST method."""
        key = req.get_param('key')
        value = req.get_param('value')
        resp.text = f'Audited - {key} {value}'
        resp.set_header('content-type', 'application/json')


app_udp_syslog_logger_1 = falcon.App(middleware=[AuditMiddleware(providers=udp_providers)])
app_udp_syslog_logger_1.add_route('/middleware', UdpSysLogResource1())


class UdpSysLogResource2:
    """Audit middleware testing resource."""

    # update global audit_controls
    audit_control = {
        'enabled': True,
        'syslog': {
            'enabled': True,
            'req_fields': {'request_access_route': 'access_route.0'},
            'resource_fields': {},
        },
    }

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        key = req.get_param('key')
        resp.text = f'Audited - {key}'
        resp.set_header('content-type', 'application/json')

    def on_put(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support PUT method."""
        key = req.get_param('key')
        value = req.get_param('value')
        resp.text = f'Audited - {key} {value}'
        resp.set_header('content-type', 'application/json')


app_udp_syslog_logger_2 = falcon.App(middleware=[AuditMiddleware(providers=udp_providers)])
app_udp_syslog_logger_2.add_route('/middleware', UdpSysLogResource2())
