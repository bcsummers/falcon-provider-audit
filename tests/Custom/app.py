"""Falcon app used for testing."""
# third-party
import falcon

# first-party
from falcon_provider_audit.middleware import AuditMiddleware
from falcon_provider_audit.utils import RotatingLoggerAuditProvider

from .db_provider import DbAuditProvider

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
        'response_status': 'status',
        'response_x_cache': 'headers.x-cache',
    },
    'resource_fields': {'user_id': 'user_id', 'my_audit_data': 'my_audit_data'},
}


class DbResource1:
    """Memcache middleware testing resource."""

    my_audit_data = None

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        key: str = req.get_param('key')
        resp.text = f'Audited - {key}'
        resp.set_header('content-type', 'application/json')
        self.my_audit_data = key  # additional data to be added to audit event

    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support POST method."""
        key: str = req.get_param('key')
        value: str = req.get_param('value')
        resp.text = f'Audited - {key} {value}'
        resp.set_header('content-type', 'application/json')


providers = [DbAuditProvider(audit_control=audit_control)]

app_db_1 = falcon.App(middleware=[AuditMiddleware(providers=providers)])
app_db_1.add_route('/middleware', DbResource1())


class DualResource1:
    """Memcache middleware testing resource."""

    my_audit_data = None

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        key: str = req.get_param('key')
        resp.text = f'Audited - {key}'
        resp.set_header('content-type', 'application/json')
        self.my_audit_data = key  # additional data to be added to audit event

    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support POST method."""
        key: str = req.get_param('key')
        value: str = req.get_param('value')
        resp.text = f'Audited - {key} {value}'
        resp.set_header('content-type', 'application/json')


providers = [
    DbAuditProvider(audit_control=audit_control),
    RotatingLoggerAuditProvider(
        audit_control=audit_control, filename='dual-audit.log', logger_name='DUAL'
    ),
]

app_dual_1 = falcon.App(middleware=[AuditMiddleware(providers=providers)])
app_dual_1.add_route('/middleware', DualResource1())


class DualResource2:
    """Memcache middleware testing resource."""

    # disable db audit provider
    audit_control = {'db': {'enabled': False}}
    my_audit_data = None

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support GET method."""
        key: str = req.get_param('key')
        resp.text = f'Audited - {key}'
        resp.set_header('content-type', 'application/json')
        self.my_audit_data = key  # additional data to be added to audit event

    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        """Support POST method."""
        key: str = req.get_param('key')
        value: str = req.get_param('value')
        resp.text = f'Audited - {key} {value}'
        resp.set_header('content-type', 'application/json')


providers = [
    DbAuditProvider(audit_control=audit_control),
    RotatingLoggerAuditProvider(
        audit_control=audit_control, filename='dual-audit.log', logger_name='DUAL'
    ),
]

app_dual_2 = falcon.App(middleware=[AuditMiddleware(providers=providers)])
app_dual_2.add_route('/middleware', DualResource2())
