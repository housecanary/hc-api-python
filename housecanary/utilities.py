"""Utility functions for hc-api-python"""

from datetime import datetime

def get_readable_time_string(seconds):
    """Returns human readable string from number of seconds"""
    seconds = int(seconds)
    minutes = seconds / 60
    seconds = seconds % 60
    hours = minutes / 60
    minutes = minutes % 60
    days = hours / 24
    hours = hours % 24

    result = ""
    if days > 0:
        result += "%d %s " % (days, "Day" if (days == 1) else "Days")
    if hours > 0:
        result += "%d %s " % (hours, "Hour" if (hours == 1) else "Hours")
    if minutes > 0:
        result += "%d %s " % (minutes, "Minute" if (minutes == 1) else "Minutes")
    if seconds > 0:
        result += "%d %s " % (seconds, "Second" if (seconds == 1) else "Seconds")

    return result.strip()


def get_datetime_from_timestamp(timestamp):
    """Return datetime from unix timestamp"""
    try:
        return datetime.fromtimestamp(int(timestamp))
    except:
        return None


def get_rate_limits(response):
    """Returns a list of rate limit information from a given response's headers."""
    periods = response.headers['X-RateLimit-Period']
    if not periods:
        return []

    rate_limits = []

    periods = periods.split(',')
    limits = response.headers['X-RateLimit-Limit'].split(',')
    remaining = response.headers['X-RateLimit-Remaining'].split(',')
    reset = response.headers['X-RateLimit-Reset'].split(',')

    for idx, period in enumerate(periods):
        rate_limit = {}
        limit_period = get_readable_time_string(period)
        rate_limit["period"] = limit_period
        rate_limit["period_seconds"] = period
        rate_limit["request_limit"] = limits[idx]
        rate_limit["requests_remaining"] = remaining[idx]

        reset_datetime = get_datetime_from_timestamp(reset[idx])
        rate_limit["reset"] = reset_datetime

        right_now = datetime.now()
        if (reset_datetime is not None) and (right_now < reset_datetime):
            # add 1 second because of rounding
            seconds_remaining = (reset_datetime - right_now).seconds + 1
        else:
            seconds_remaining = 0

        rate_limit["reset_in_seconds"] = seconds_remaining

        rate_limit["time_to_reset"] = get_readable_time_string(seconds_remaining)
        rate_limits.append(rate_limit)

    return rate_limits
