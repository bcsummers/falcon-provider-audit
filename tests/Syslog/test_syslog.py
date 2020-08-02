# -*- coding: utf-8 -*-
"""Test hooks feature of falcon_provider_memcache module."""
# standard library
import os
import time
from uuid import uuid4

# third-party
from falcon.testing.client import Result

# required for monkeypatch
from .app import TcpSysLogResource1, TcpSysLogResource2, UdpSysLogResource1, UdpSysLogResource2


def has_text(logfile: str, text: str) -> bool:
    """Search for unique text in log file.

    Args:
        logfile: The fully qualified path to the logfile.
        text: The text to search for in the logfile.

    Returns:
        bool: True if text is found, else False.
    """
    time.sleep(0.10)  # allow time for log to flush
    with open(logfile, 'r') as fh:
        for line in fh.read().strip().split('\n'):
            if text in line:
                break
        else:
            return False
    return True


def test_tcp_syslog_1(client_tcp_logger_1: object, log_directory: str, monkeypatch: object):
    """Testing GET resource

    Args:
        client_tcp_logger_1 (fixture): The test client.
        log_directory (fixture): The fully qualified path for the log directory.
        monkeypatch (fixture): The monkeypatch object.
    """
    logfile: str = os.path.join(log_directory, 'syslog_server.log')
    monkeypatch.setattr(TcpSysLogResource1, 'user_id', 123, raising=False)

    key = f'{uuid4()}'
    params = {'key': key}
    response: Result = client_tcp_logger_1.simulate_get('/middleware', params=params)
    assert response.status_code == 200
    assert response.text == f'Audited - {key}'
    assert has_text(logfile, key) is True, f'Failed to find key {key}'


def test_tcp_syslog_2(client_tcp_logger_2: object, log_directory: str, monkeypatch: object):
    """Testing POST resource

    Args:
        client_tcp_logger_2 (fixture): The test client.
        log_directory (fixture): The fully qualified path for the log directory.
        monkeypatch (fixture): The monkeypatch object.
    """
    logfile: str = os.path.join(log_directory, 'syslog_server.log')
    monkeypatch.setattr(TcpSysLogResource2, 'user_id', 123, raising=False)

    key = f'{uuid4()}'
    params = {'key': key, 'value': 'middleware-worked'}
    response: Result = client_tcp_logger_2.simulate_put('/middleware', params=params)
    assert response.status_code == 200
    assert response.text == f'Audited - {key} middleware-worked'
    assert (
        has_text(logfile, 'request_access_route') is True
    ), 'Failed to find value "request_access_route"'


def test_udp_syslog_1(client_udp_logger_1: object, log_directory: str, monkeypatch: object):
    """Testing GET resource

    Args:
        client_udp_logger_1 (fixture): The test client.
        log_directory (fixture): The fully qualified path for the log directory.
        monkeypatch (fixture): The monkeypatch object.
    """
    logfile: str = os.path.join(log_directory, 'syslog_server.log')
    monkeypatch.setattr(UdpSysLogResource1, 'user_id', 123, raising=False)

    key = f'{uuid4()}'
    params = {'key': key}
    response: Result = client_udp_logger_1.simulate_get('/middleware', params=params)
    assert response.status_code == 200
    assert response.text == f'Audited - {key}'
    assert has_text(logfile, key) is True, f'Failed to find key {key}'


def test_udp_syslog_2(client_udp_logger_2: object, log_directory: str, monkeypatch: object):
    """Testing POST resource

    Args:
        client_udp_logger_2 (fixture): The test client.
        log_directory (fixture): The fully qualified path for the log directory.
        monkeypatch (fixture): The monkeypatch object.
    """
    logfile: str = os.path.join(log_directory, 'syslog_server.log')
    monkeypatch.setattr(UdpSysLogResource2, 'user_id', 123, raising=False)

    key = f'{uuid4()}'
    params = {'key': key, 'value': 'middleware-worked'}
    response: Result = client_udp_logger_2.simulate_put('/middleware', params=params)
    assert response.status_code == 200
    assert response.text == f'Audited - {key} middleware-worked'
    assert (
        has_text(logfile, 'request_access_route') is True
    ), 'Failed to find value "request_access_route"'
