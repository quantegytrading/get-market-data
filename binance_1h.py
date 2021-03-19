# binance_commons.py
import calendar
from datetime import datetime
from binance_commons import go


def main(event, context):
    now = datetime.utcnow()
    unixtime = calendar.timegm(now.utctimetuple())
    # (unixtime - num of hours * sixty mins * sixty seconds) * 1000 ms
    since = (unixtime - 24 * 60 * 60) * 1000  # UTC timestamp in milliseconds
    go('1h', since)


if __name__ == "__main__":
    main('', '')