import time
from datetime import datetime as dt

def format_currency(amount):
    if abs(amount) >= 1e9:
        return f"${amount / 1e9:.2f}B"
    elif abs(amount) >= 1e6:
        return f"${amount / 1e6:.2f}M"
    else:
        return f"${amount:,.2f}"

def get_string_date_from_time(timestamp: float) -> str:
    datetime = dt.fromtimestamp(timestamp)
    string_date = datetime.strftime("%Y-%m-%d %H:%M:%S")
    return string_date