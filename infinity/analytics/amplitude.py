import requests
import json

from infinity.analytics.base import Analytics


class AmplitudeAnalytics(Analytics):
    """
    Implementation of Analytics for Amplitude
    """
    def __init__(self):
        self.api_key = '7742bd5030d4eb3a58b7c78277c2958c'

    def invoke_register_user(self, user_id, user_properties):
        identification = [
            {
                "user_id": user_id,
                "user_properties": user_properties,
            }
        ]

        request_data = {
            "api_key": self.api_key,
            "identification": json.dumps(identification)
        }

        response = requests.post(url='https://api.amplitude.com/identify', data=request_data)
        return response

    def invoke_track_event(self, user_id, event_name, event_properties):
        request_data = {
            "api_key": self.api_key,
            "events": [
                {
                    "user_id": user_id,
                    "event_type": event_name,
                    "event_properties": event_properties,
                }
            ]
        }

        response = requests.post(url='https://api.amplitude.com/2/httpapi', data=json.dumps(request_data))
        return response