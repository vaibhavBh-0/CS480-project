import time
from datetime import datetime as dt


def get_string_date_from_time(timestamp: float) -> str:
    datetime = dt.fromtimestamp(timestamp)
    string_date = datetime.strftime("%Y-%m-%d %H:%M:%S")
    return string_date