# Infinity follows similar strategy as Homebrew
# https://github.com/Homebrew/brew/blob/bbed7246bc5c5b7acb8c1d427d10b43e090dfd39/docs/Analytics.md

import abc
import platform
import time
import uuid

from infinity.settings import get_infinity_settings, update_infinity_settings


def swallow_exceptions(func):
    """
    Decorator that swallows exceptions and does not propage it
    Used in non-critical code paths like analytics update
    """
    def updated_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:  # noqa
            pass

    return updated_func


class Analytics(abc.ABC):

    @abc.abstractmethod
    def invoke_register_user(self, user_id, user_properties):
        pass

    @swallow_exceptions
    def register_user(self):
        # Get or create new User ID
        user_id = get_infinity_settings().get('user_id_analytics')
        if not user_id:
            user_id = str(uuid.uuid1())
            update_infinity_settings(
                {
                    "user_id_analytics": user_id
                }
            )

        # Get user and machine info
        user_properties = {
            "os_name": platform.system(),
            "os_version": platform.release(),
            "python_version": platform.python_version(),
            "timezone": time.tzname[0],
        }

        self.invoke_register_user(user_id=user_id, user_properties=user_properties)
        return user_id

    @abc.abstractmethod
    def invoke_track_event(self, user_id, event_name, event_properties):
        pass

    @swallow_exceptions
    def track_event(self, event_name, event_properties={}):
        user_id = get_infinity_settings().get('user_id_analytics')
        if not user_id:
            user_id = self.register_user()

        self.invoke_track_event(user_id=user_id,
                                event_name=event_name,
                                event_properties=event_properties)