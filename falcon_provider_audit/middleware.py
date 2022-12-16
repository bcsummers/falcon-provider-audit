"""Falcon audit middleware module."""

# third-party
import falcon


class AuditMiddleware:
    """Audit middleware provider."""

    def __init__(self, providers: list[object], user_id=None):
        """Initialize class properties.

        Args:
            providers: A list of audit providers.
            user_id: The falcon resource property that contains the unique
                username or userid that will be written in audit event.
        """
        self.providers = providers
        self.user_id = user_id

    def process_resource(  # pylint: disable=unused-argument
        self, req: falcon.Request, resp: falcon.Response, resource: object, params: dict
    ) -> None:
        """Process the request after routing and provide caching service."""
        # update the audit control for the current resource
        audit_control = {}
        if hasattr(resource, 'audit_control') and isinstance(resource.audit_control, dict):
            audit_control = resource.audit_control

        # stop if auditing is explicitly set to False
        if audit_control.get('enabled') is False:
            resp.context['audit'] = False
            return

        resp.context['audit'] = True
        for provider in self.providers:
            # update audit control for each provider
            provider.audit_control(audit_control)

    def process_response(  # pylint: disable=unused-argument
        self, req: falcon.Request, resp: falcon.Response, resource: object, req_succeeded: bool
    ) -> None:
        """Process the request after routing and provide audit services.

        audit_control = {
            'req_fields': {
                'request_access_route': 'access_route',
                'request_forwarded_host': 'forwarded_host'
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
                'response_content_length': 'headers.content_length',
                'response_content_type': 'headers.content_type',
                'response_x_cache': 'headers.X-Cache',
                'response_status': 'status',
            }
            'resource_fields': {'user_id': 'user_id'}
            'provider_names': None,
        }
        """
        if resp.context.get('audit') is not True:
            return

        # each provider can have different settings
        for provider in self.providers:
            if provider.enabled is False:
                # skip disabled providers
                continue

            event_data = {}

            # handle req data
            req_data: dict = self.get_event_data(provider.req_fields, req)
            event_data.update(req_data)

            # handle resource data
            resource_data: dict = self.get_event_data(provider.resource_fields, resource)
            event_data.update(resource_data)

            # handle resp data
            resp_data: dict = self.get_event_data(provider.resp_fields, resp)
            event_data.update(resp_data)

            # add event data
            provider.add_event(event_data)

    def get_event_data(self, field_dict: dict, obj: object) -> dict:
        """Get event data from provided object.

        Extremely basic pathing support. There doesn't appear to be very many complex data
        structures in the 3 Falcon object so support for a more featured tool like jmespath
        or jq doesn't seem to be necessary at this time.

        Args:
            field_dict: The dictionary containing label and field names.
            obj: The falcon object containing the data.

        Returns:
            dict: The dictionary containing the audit data.
        """
        event_data = {}
        for label, field in field_dict.items():
            key1, key2 = self.key_value(field)
            try:
                data: dict | list | str = getattr(obj, key1)

                if field.startswith('context.') and hasattr(obj, 'context'):
                    event_data[label] = self.get_event_data_context(field, obj)
                elif isinstance(data, dict) and key2 is not None:
                    # handle nested dict (e.g., headers)
                    event_data[label] = data.get(key2)
                elif isinstance(data, list) and key2 is not None:
                    event_data[label] = self.get_event_data_list(data, key2)
                else:
                    event_data[label] = data
            except AttributeError:  # pragma: no cover
                # TODO: add logging
                event_data[label] = None
        return event_data

    @staticmethod
    def get_event_data_context(field: str, obj: object) -> dict | list | str:
        """Get event data from nested context object in req.

        Args:
            field: The field to lookup.
            obj: The falcon object containing the data.

        Returns:
            Any: The value from the object.
        """
        # special case for nested context object in req
        try:
            return getattr(obj.context, field.lstrip('context.'))
        except Exception:  # pylint: disable=broad-except
            return None

    @staticmethod
    def get_event_data_list(data: list, key2: str) -> dict | list | str:
        """Get event data from list by index value.

        Args:
            data: The list to pull data via index.
            key2: The index to retrieve.

        Returns:
            Any: The value from the object.
        """
        try:
            return data[int(key2)]
        except (IndexError, ValueError):  # pragma: no cover
            # TODO: add logging
            return None

    @staticmethod
    def key_value(field: str) -> tuple:
        """Return key value for field.

        Only a single "." is supported in field.

        Args:
            field: The field name containing a ".".

        Returns:
            tuple: The field keys split on ".".
        """
        try:
            fields = field.split('.', 1)
            return fields[0], fields[1]
        except IndexError:
            return field, None
