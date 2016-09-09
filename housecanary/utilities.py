"""Utility functions for hc-api-python"""

from datetime import datetime

def get_readable_time_string(seconds):
    """Returns human readable string from number of seconds"""
    minutes = int(seconds) / 60
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

    return result.strip()


def get_datetime_from_timestamp(timestamp):
    """Converts unix timestamp to a more readable datetime format"""
    return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')


def get_rate_limits(response):
    """Returns a list of rate limit information from a given response's headers."""
    rate_limits = []

    periods = response.headers['X-RateLimit-Period'].split(',')
    limits = response.headers['X-RateLimit-Limit'].split(',')
    remaining = response.headers['X-RateLimit-Remaining'].split(',')
    reset = response.headers['X-RateLimit-Reset'].split(',')

    for idx, period in enumerate(periods):
        rate_limit = {}
        limit_period = get_readable_time_string(period)
        rate_limit["period"] = limit_period
        rate_limit["limit"] = limits[idx]
        rate_limit["remaining"] = remaining[idx]
        rate_limit["reset"] = get_datetime_from_timestamp(reset[idx])
        rate_limits.append(rate_limit)

    return rate_limits
