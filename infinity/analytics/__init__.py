from infinity.analytics.local import LocalAnalytics
from infinity.analytics.amplitude import AmplitudeAnalytics
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