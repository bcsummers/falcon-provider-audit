"""Test hooks feature of falcon_provider_memcache module."""
# standard library
import os
from uuid import uuid4

# third-party
from falcon.testing import Result

# required for monkeypatch
from .app import RotatingLoggerResource1, RotatingLoggerResource2


def has_text(logfile: str, text: str) -> bool:
    """Search for unique text in log file.

    Args:
        logfile: The fully qualified path to the logfile.
        text: The text to search for in the logfile.

    Returns:
        bool: True if text is found, else False.
    """
    with open(logfile, encoding='utf-8') as fh:
        for line in fh.read().strip().split('\n'):
            if text in line:
                break
        else:
            return False
    return True


def test_default_get(client_rotating_logger_1: object, log_directory: str, monkeypatch: object):
    """Testing GET resource

    Args:
        client_rotating_logger_1 (fixture): The test client.
        log_directory (fixture): The fully qualified path for the log directory.
        monkeypatch (fixture): The monkeypatch object.
    """
    monkeypatch.setattr(RotatingLoggerResource1, 'user_id', 123, raising=False)

    logfile: str = os.path.join(log_directory, 'audit.log')
    key = f'{uuid4()}'
    params = {'key': key}
    response: Result = client_rotating_logger_1.simulate_get('/middleware', params=params)
    assert response.status_code == 200
    assert response.text == f'Audited - {key}'
    # validate log file
    assert os.path.isfile(logfile)
    assert os.stat(logfile).st_size != 0
    assert has_text(logfile, key) is True  # search for unique string in logfile


def test_default_post(client_rotating_logger_1: object, log_directory: str, monkeypatch: object):
    """Testing POST resource

    Args:
        client_rotating_logger_1 (fixture): The test client.
        log_directory (fixture): The fully qualified path for the log directory.
        monkeypatch (fixture): The monkeypatch object.
    """
    monkeypatch.setattr(RotatingLoggerResource1, 'user_id', 123, raising=False)

    logfile: str = os.path.join(log_directory, 'audit.log')
    key = f'{uuid4()}'
    params = {'key': key, 'value': 'middleware-worked'}
    response: Result = client_rotating_logger_1.simulate_post('/middleware', params=params)
    assert response.status_code == 200
    assert response.text == f'Audited - {key} middleware-worked'
    assert os.path.isfile(logfile)
    assert has_text(logfile, key) is True  # search for unique string in logfile


def test_default_put(client_rotating_logger_2: object, log_directory: str, monkeypatch: object):
    """Testing PUT resource

    Args:
        client_rotating_logger_2 (fixture): The test client.
        log_directory (fixture): The fully qualified path for the log directory.
        monkeypatch (fixture): The monkeypatch object.
    """
    user_id = f'{uuid4()}'  # unique value to check for in logs
    monkeypatch.setattr(RotatingLoggerResource2, 'user_id', user_id, raising=False)

    logfile: str = os.path.join(log_directory, 'audit.log')
    key = f'{uuid4()}'
    params = {'key': key, 'value': 'middleware-worked'}
    response: Result = client_rotating_logger_2.simulate_put('/middleware', params=params)
    assert response.status_code == 200
    assert response.text == f'Audited - {key} middleware-worked'
    # validate log file
    assert os.path.isfile(logfile)
    assert os.stat(logfile).st_size != 0

    # ensure user_id is not logged due to audit_control override on resource
    assert has_text(logfile, user_id) is False


def test_disabled(client_rotating_logger_2: object, log_directory: str, monkeypatch: object):
    """Disable rate limit.

    Args:
        client_rotating_logger_2 (fixture): The test client.
        log_directory (fixture): The fully qualified path for the log directory.
        monkeypatch (fixture): The monkeypatch object.
    """
    user_id = f'{uuid4()}'  # unique value to check for in logs
    monkeypatch.setattr(RotatingLoggerResource2, 'user_id', user_id, raising=False)
    # disable auditing
    monkeypatch.setitem(RotatingLoggerResource2.audit_control, 'enabled', False)

    logfile: str = os.path.join(log_directory, 'audit.log')
    key = f'{uuid4()}'
    params = {'key': key, 'value': 'middleware-worked'}
    response: Result = client_rotating_logger_2.simulate_put('/middleware', params=params)
    assert response.status_code == 200
    assert response.text == f'Audited - {key} middleware-worked'
    # validate log file
    assert os.path.isfile(logfile)
    assert os.stat(logfile).st_size != 0

    # ensure user_id is not logged due to audit_control override on resource
    assert has_text(logfile, user_id) is False
    assert has_text(logfile, key) is False
