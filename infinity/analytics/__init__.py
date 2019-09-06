from infinity.analytics.local import LocalAnalytics
from infinity.analytics.amplitude import AmplitudeAnalytics
from infinity.analytics.sentry import initialize_sentry
from infinity.settings import get_infinity_settings

client = None


def get_analytics_client():
    global client
    if not client:
        debug_mode = get_infinity_settings().get('infinity_debug_mode')
        if debug_mode:
            client = LocalAnalytics()
        else:
            client = AmplitudeAnalytics()

    return client


def initialize_raven_client():
    debug_mode = get_infinity_settings().get('infinity_debug_mode')
    if not debug_mode:
        # TODO: Sentry prints verbose message on all exceptions
        # Infinity throws valid exceptions from boto. So this is distracting

        # initialize_sentry()
        pass