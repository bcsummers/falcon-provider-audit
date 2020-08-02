# -*- coding: utf-8 -*-
"""Audit middleware module."""
# standard library
from datetime import datetime
from typing import Optional

# third-party
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# first-party
from falcon_provider_audit import AuditProvider

engine = db.create_engine('sqlite:///:memory:', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class AuditModel(Base):
    """Database App Model."""

    __tablename__ = 'audit'
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    request_access_route = db.Column(db.String(100), nullable=True)
    request_forwarded_host = db.Column(db.String(100), nullable=True)
    request_host = db.Column(db.String(100), nullable=True)
    request_method = db.Column(db.String(20), nullable=True)
    request_path = db.Column(db.String(500), nullable=True)
    request_port = db.Column(db.Integer, nullable=True)
    request_query_string = db.Column(db.String(500), nullable=True)
    request_referer = db.Column(db.String(200), nullable=True)
    request_remote_addr = db.Column(db.String(100), nullable=True)
    request_scheme = db.Column(db.String(20), nullable=True)
    request_user_agent = db.Column(db.String(200), nullable=True)
    response_content_length = db.Column(db.Integer, default=0)
    response_content_type = db.Column(db.String(100), nullable=True)
    response_status = db.Column(db.String(100), nullable=True)
    response_x_cache = db.Column(db.String(20), nullable=True)
    user_id = db.Column(db.String(100), nullable=True)
    my_audit_data = db.Column(db.String(100), nullable=True)


AuditModel.__table__.create(engine)  # pylint: disable=no-member


class DbAuditProvider(AuditProvider):
    """Database Audit Provider.

    Args:
        audit_control: A default audit control object.
    """

    def __init__(self, audit_control: Optional[dict] = None):
        """Initialize class properties"""
        super().__init__(audit_control)

        # property
        self._name = 'db'

    def add_event(self, event: dict) -> None:
        """Add an audit event.

        Args:
            event: The event data.
        """
        if self.providers is None or (
            isinstance(self.providers, list) and self.name in self.providers
        ):
            # covert list to string for sqlite, for postgres possible use JSON column type
            event['request_access_route'] = ','.join(event.get('request_access_route'))
            try:
                ae = AuditModel(**event)
                session.add(ae)  # pylint: disable=no-member
                session.commit()  # pylint: disable=no-member
            except Exception:  # pragma: no cover; pylint: disable=broad-except
                # appropriately handle db error
                pass
