# -*- coding: utf-8 -*-
"""Test hooks feature of falcon_provider_memcache module."""
# standard library
import os
from uuid import uuid4

# third-party
from falcon.testing import Result

# required for monkeypatch
from .app import DualResource1
from .db_provider import AuditModel, session


def has_text(logfile: str, text: str) -> bool:
    """Search for unique text in log file.

    Args:
        logfile: The fully qualified path to the logfile.
        text: The text to search for in the logfile.

    Returns:
        bool: True if text is found, else False.
    """
    with open(logfile, 'r') as fh:
        for line in fh.read().strip().split('\n'):
            if text in line:
                break
        else:
            return False
    return True


def test_dual_get(client_dual_1: object, log_directory: str, monkeypatch: object) -> None:
    """Testing dual audit providers.

    Args:
        client_dual_1 (fixture): The test client.
        log_directory (fixture): The fully qualified path for the log directory.
        monkeypatch (fixture): The monkeypatch object.
    """
    monkeypatch.setattr(DualResource1, 'user_id', 123, raising=False)

    logfile: str = os.path.join(log_directory, 'dual-audit.log')
    key = f'{uuid4()}'
    params = {'key': key}
    response: Result = client_dual_1.simulate_get('/middleware', params=params)
    assert response.status_code == 200
    assert response.text == f'Audited - {key}'

    # check db
    row: object = (
        session.query(AuditModel).filter_by(my_audit_data=key).first()  # pylint: disable=no-member
    )
    # assert row.id == 1
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
    # check logfile
    assert has_text(logfile, key) is True  # search for unique string in logfile


def test_dual_disable_get(client_dual_2: object, log_directory: str, monkeypatch: object) -> None:
    """Testing dual audit provider with one disabled on resource.

    Args:
        client_dual_2 (fixture): The test client.
        log_directory (fixture): The fully qualified path for the log directory.
        monkeypatch (fixture): The monkeypatch object.
    """
    monkeypatch.setattr(DualResource1, 'user_id', 123, raising=False)

    logfile: str = os.path.join(log_directory, 'dual-audit.log')
    key = f'{uuid4()}'
    params = {'key': key}
    response: Result = client_dual_2.simulate_get('/middleware', params=params)
    assert response.status_code == 200
    assert response.text == f'Audited - {key}'

    # check db
    row: object = (
        session.query(AuditModel).filter_by(my_audit_data=key).first()  # pylint: disable=no-member
    )
    assert row is None  # nothing should be written to DB
    # check logfile
    assert has_text(logfile, key) is True  # search for unique string in logfile
