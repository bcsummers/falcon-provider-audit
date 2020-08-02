# -*- coding: utf-8 -*-
"""Testing conf module."""
# standard library
import os
import threading

# third-party
import pytest
from falcon import testing

from .Custom.app import app_db_1, app_dual_1, app_dual_2
from .Syslog.syslog_server import TestSyslogServers

# the log directory for all test cases
_LOG_DIRECTORY = os.path.join(os.getcwd(), 'log')
test_syslog = TestSyslogServers(address='0.0.0.0', log_directory=_LOG_DIRECTORY)
tcp_server = test_syslog.start_tcp_server(port=5141)
udp_server = test_syslog.start_udp_server(port=5140)


@pytest.fixture
def client_db_1():
    """Create testing client"""
    return testing.TestClient(app_db_1)


@pytest.fixture
def client_dual_1():
    """Create testing client"""
    return testing.TestClient(app_dual_1)


@pytest.fixture
def client_dual_2():
    """Create testing client"""
    return testing.TestClient(app_dual_2)


@pytest.fixture
def client_rotating_logger_1():
    """Create testing client"""
    from .Rotating_Logger.app import (  # pylint: disable=import-outside-toplevel
        app_rotating_logger_1,
    )

    return testing.TestClient(app_rotating_logger_1)


@pytest.fixture
def client_rotating_logger_2():
    """Create testing client"""
    from .Rotating_Logger.app import (  # pylint: disable=import-outside-toplevel
        app_rotating_logger_2,
    )

    return testing.TestClient(app_rotating_logger_2)


@pytest.fixture
def client_tcp_logger_1():
    """Create testing client"""
    from .Syslog.app import app_tcp_syslog_logger_1  # pylint: disable=import-outside-toplevel

    return testing.TestClient(app_tcp_syslog_logger_1)


@pytest.fixture
def client_tcp_logger_2():
    """Create testing client"""
    from .Syslog.app import app_tcp_syslog_logger_2  # pylint: disable=import-outside-toplevel

    return testing.TestClient(app_tcp_syslog_logger_2)


@pytest.fixture
def client_udp_logger_1():
    """Create testing client"""
    from .Syslog.app import app_udp_syslog_logger_1  # pylint: disable=import-outside-toplevel

    return testing.TestClient(app_udp_syslog_logger_1)


@pytest.fixture
def client_udp_logger_2():
    """Create testing client"""
    from .Syslog.app import app_udp_syslog_logger_2  # pylint: disable=import-outside-toplevel

    return testing.TestClient(app_udp_syslog_logger_2)


@pytest.fixture
def log_directory():
    """Return the log directory"""
    return _LOG_DIRECTORY


def pytest_configure():
    """Clear the log directory after tests are complete"""
    # start TCP syslog servers
    tcp_thread = threading.Thread(name='tcp_server', target=tcp_server.serve_forever, daemon=True)
    tcp_thread.start()

    # start UDP syslog servers
    udp_thread = threading.Thread(name='udp_server', target=udp_server.serve_forever, daemon=True)
    udp_thread.start()


def pytest_unconfigure(config):  # pylint: disable=unused-argument
    """Clear the log directory after tests are complete"""
    if os.path.isdir(_LOG_DIRECTORY):
        for log_file in os.listdir(_LOG_DIRECTORY):
            file_path = os.path.join(_LOG_DIRECTORY, log_file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        os.rmdir(_LOG_DIRECTORY)
