"""Translate user-facing exceptions at the UI boundary, preserving diagnostics."""
from app.shared.translations import get_catalog


class UserMessageError(ValueError):
    def __init__(self, message_id, **parameters):
        self.message_id, self.parameters = message_id, parameters
        # Keep the conventional English exception text for logs and integrations.
        super().__init__(get_catalog('English').get(message_id, message_id).format(**parameters))


def error_text(error, translate):
    if isinstance(error, UserMessageError):
        parameters = dict(error.parameters)
        if 'language' in parameters:
            from app.shared.languages import legacy_name
            try: parameters['language'] = translate(legacy_name(parameters['language']))
            except KeyError: pass
        return translate(error.message_id).format(**parameters)
    message = str(error)
    if message in get_catalog('English'):
        return translate(message)
    # OS/device/provider diagnostics cannot be fully translated. Give them an
    # explicit localized context instead of presenting bare exception prose.
    return translate('Operation failed. Details: {details}').format(details=message)
