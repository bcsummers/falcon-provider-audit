"""Audit middleware module."""
# standard library
import logging
import os
import socket
from logging.handlers import RotatingFileHandler


class RotatingFileHandlerCustom(RotatingFileHandler):
    """Customized Rotating handler that will ensure log directory path is created."""

    def __init__(
        self,
        filename: str,
        mode: str | None = 'a',
        maxBytes: int | None = 0,
        backupCount: int | None = 0,
        encoding: str | None = None,
        delay: int | None = 0,
    ):
        """Customize RotatingFileHandler to create full log path.

        Args:
            filename: The name of the logfile.
            mode: The write mode for the file.
            maxBytes: The max file size before rotating.
            backupCount: The maximum number of backup files.
            encoding: The log file encoding.
            delay: The delay period.
        """
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount, encoding, delay)


class AuditProvider:
    """Base Audit Provider Class.

    Args:
        audit_control: A default audit control object.
    """

    def __init__(self, audit_control: dict | None = None):
        """Initialize class properties

        **Audit Control**

        enabled (bool): Turns auditing on or off for the current resource or globally.
        req_fields (dict): A dict of label and field names from the req object that should be
            added to the audit event. A None value or empty dict indicates that no value from this
            object should be added to audit event.
        resource_fields (dict): A dict of label and field names from the resource object that should
            be added to the audit event. A None value or empty dict indicates that no value from
            this object should be added to audit event.
        resp_fields (dict): A dict of label and field names from the resp object that should be
            added to the audit event. A None value or empty dict indicates that no value from this
            object should be added to audit event.
        provider_names (list): A list of audit providers that the audit event should be written. If
            a None value is provided the event will be sent to all audit providers.

        .. code:: python

            class ApiResource:
                audit_control = {
                    'enabled': True,
                    'req_fields': {},
                    'resource_fields': {},
                    'resp_fields': {},
                    'provider_names': None,
                }
                def on_get(self, req, resp):
                    ...
        """
        self._global_audit_control = {
            'enabled': False,
            'resource_fields': [],
            'req_fields': [],
            'resp_fields': [],
            'providers': None,
        }
        if audit_control is not None:
            # update global audit control with user provided settings
            self._global_audit_control.update(audit_control)
        self._audit_control = dict(self._global_audit_control)

        # property
        self._name = None

    def add_event(self, event: dict) -> None:  # pragma: no cover
        """Add audit event"""
        raise NotImplementedError('This method must be implemented in child class.')

    def audit_control(self, audit_control: dict | None = None) -> dict:
        """Return audit control settings.

        Args:
            audit_control: The audit control settings.

        Returns:
            dict: Updated audit control settings.
        """
        audit_control = audit_control or {}
        self._audit_control = dict(self._global_audit_control)

        # handle updates per provider name
        if audit_control.get(self.name) is not None:
            audit_control: dict = audit_control.get(self.name)

        self._audit_control.update(audit_control)
        return self._audit_control

    @property
    def enabled(self) -> bool:
        """Return audit control enabled value."""
        return self._audit_control.get('enabled', False)

    @property
    def name(self) -> str:
        """Return provider name."""
        return self._name

    @property
    def providers(self) -> list:
        """Return audit control providers value."""
        return self._audit_control.get('providers')

    @property
    def req_fields(self) -> dict:
        """Return audit control req_fields value."""
        return self._audit_control.get('req_fields') or {}

    @property
    def resource_fields(self) -> dict:
        """Return audit control resource_fields value."""
        return self._audit_control.get('resource_fields') or {}

    @property
    def resp_fields(self) -> dict:
        """Return audit control resp_fields value."""
        return self._audit_control.get('resp_fields') or {}


class RotatingLoggerAuditProvider(AuditProvider):
    """Logger Audit Provider.

    Args:
        audit_control: A default audit control object.
        backup_count: The number of backup log files to keep.
        directory: The directory to write the log file.
        filename: The name of the log file.
        formatter: A logging formatter to format logging handler.
            Defaults to a sane formatter with module/lineno.
        formatter: A sane formatter with module/lineno. A logging
            formatter to format logging handler.
        level: The level for the logger.
        logger_name: The logger name as displayed in the log file.
        max_bytes: The maximum size of the log file.
        mode: The write mode for the log file.
    """

    def __init__(
        self,
        audit_control: dict | None = None,
        backup_count: int | None = 10,
        directory: str | None = 'log',
        filename: str | None = 'audit.log',
        formatter: logging.Formatter | None = None,
        level: str | None = 'INFO',
        logger_name: str | None = 'AUDIT',
        max_bytes: int | None = 10_485_760,
        mode: str | None = 'a',
    ):
        """Initialize class properties"""
        super().__init__(audit_control)
        self.backup_count = backup_count
        self.directory = directory
        self.filename = filename
        self.formatter = formatter
        self.level = level.upper()
        self.logger_name = logger_name
        self.max_bytes = max_bytes
        self.mode = mode

        # property
        self._name = 'rotating_logger'

        # get logger
        self.log = self._init_logger()

    def _init_logger(self):
        """Initialize class logger."""
        logger = logging.getLogger(self.logger_name)
        fh = RotatingFileHandlerCustom(
            os.path.join(self.directory, self.filename),
            backupCount=self.backup_count,
            maxBytes=self.max_bytes,
            mode=self.mode,
        )
        fh.setLevel(logging.DEBUG)
        if self.formatter is None:
            # TODO: Add a JSON formatter
            self.formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s '
            )
        fh.setFormatter(self.formatter)
        fh.set_name(self.name)
        logger.addHandler(fh)
        # set level
        logger.setLevel(logging.getLevelName(self.level.upper()))

        return logger

    def add_event(self, event: dict, **kwargs):
        """Add an audit event.

        Args:
            event: The event data.
            level (kwargs): The logging level.
        """
        level: str = kwargs.get('level', 'info').lower()
        if self.providers is None or (
            isinstance(self.providers, list) and self.name in self.providers
        ):
            log = getattr(self.log, level)
            event_data = []
            for k, v in sorted(event.items()):
                if isinstance(v, list):
                    v = ','.join(v)
                event_data.append(f'{k}="{v}"')
            log(', '.join(event_data))


class SyslogAuditProvider(AuditProvider):
    """Syslog Audit Provider.

    Args:
        audit_control: A default audit control object.
        host: The syslog hostname/ip.
        facility: The syslog facility.
        formatter: A logging formatter to format logging handler.
            Defaults to a sane formatter with module/lineno.
        level: The level for the logger.
        logger_name: The logger name as displayed in the log file.
        port: The syslog port.
        socktype: The socket type. Either TCP or UDP.
    """

    def __init__(
        self,
        audit_control: dict | None = None,
        host: str | None = 'localhost',
        facility: str | None = 'user',
        formatter: logging.Formatter | None = None,
        level: str | None = 'INFO',
        logger_name: str | None = 'AUDIT',
        port: int | None = 514,
        socktype: str | None = 'UDP',
    ):
        """Initialize class properties"""
        super().__init__(audit_control)
        self.facility = facility
        self.formatter = formatter
        self.level = level.upper()
        self.logger_name = logger_name
        self.socktype = socktype

        # property
        self._name = 'syslog'
        self.address = (host, int(port))

        # get logger
        self.log = self._init_logger()

    def _init_logger(self) -> None:
        """Initialize class logger."""
        if self.socktype == 'TCP':
            self.socktype = socket.SOCK_STREAM
        else:
            self.socktype = socket.SOCK_DGRAM  # default

        logger = logging.getLogger(self.logger_name)
        lh = logging.handlers.SysLogHandler(
            address=self.address, facility=self.facility, socktype=self.socktype
        )
        lh.setLevel(logging.DEBUG)
        if self.formatter is None:
            # TODO: Add a JSON formatter
            self.formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s '
            )
        lh.setFormatter(self.formatter)
        lh.set_name(self.name)
        logger.addHandler(lh)
        # set level
        logger.setLevel(logging.getLevelName(self.level.upper()))

        return logger

    def add_event(self, event: dict, **kwargs) -> None:
        """Add an audit event.

        Args:
            event: The event data.
            level (kwargs): The logging level.
        """
        level: str = kwargs.get('level', 'info').lower()
        if self.providers is None or (
            isinstance(self.providers, list) and self.name in self.providers
        ):
            log = getattr(self.log, level)
            event_data = []
            for k, v in sorted(event.items()):
                if isinstance(v, list):
                    v = ','.join(v)
                event_data.append(f'{k}="{v}"')
            log(', '.join(event_data))
