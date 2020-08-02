# -*- coding: utf-8 -*-
"""Test hooks feature of falcon_provider_memcache module."""
# standard library
from uuid import uuid4

# third-party
from falcon.testing.client import Result

# required for monkeypatch
from .app import DbResource1
from .db_provider import AuditModel, session


def test_default_get(client_db_1: object, monkeypatch: object) -> None:
    """Testing GET resource

    Args:
        client_db_1 (fixture): The test client.
        monkeypatch (fixture): The monkeypatch object.
    """
    monkeypatch.setattr(DbResource1, 'user_id', 123, raising=False)

    key = f'{uuid4()}'
    params = {'key': key}
    response: Result = client_db_1.simulate_get('/middleware', params=params)
    assert response.status_code == 200
    assert response.text == f'Audited - {key}'

    row: object = (
        session.query(AuditModel).filter_by(my_audit_data=key).first()  # pylint: disable=no-member
    )
    assert row.request_access_route == '127.0.0.1'
    assert row.request_forwarded_host == 'falconframework.org'
    assert row.request_host == 'falconframework.org'
    assert row.request_method == 'GET'
    assert row.request_path == '/middleware'
    assert row.request_port == 80
    assert row.request_query_string == f'key={key}'
    assert row.request_referer is None
    assert row.request_remote_addr == '127.0.0.1'
    assert row.request_scheme == 'http'
    assert row.request_user_agent == 'curl/7.24.0 (x86_64-apple-darwin12.0)'
    assert row.response_content_length == 0
    assert row.response_content_type == 'application/json'
    assert row.response_status == '200 OK'
    assert row.response_x_cache is None
    assert int(row.user_id) == 123
    assert row.my_audit_data == key
