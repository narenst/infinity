from infinity.analytics.base import Analytics


class LocalAnalytics(Analytics):
    """
    Implementation of Analytics for Development.
    """
    def invoke_register_user(self, user_id, user_properties):
        print(f"Registering user: {user_id} with properties: {user_properties}")

    def invoke_track_event(self, user_id, event_name, event_properties):
        print(f"Sending event: {event_name} with properties: {event_properties}")