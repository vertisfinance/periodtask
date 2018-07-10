from datetime import datetime

import pytz


def ts(s):
    dt = datetime.strptime(s, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
    ts = (dt - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()
    return int(ts)
