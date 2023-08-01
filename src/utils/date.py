import arrow 
from datetime import datetime

def to_unix_timestamp(date_str: str) -> int:
    """
    Convert a date string to a unix timestamp (seconds since epoch).

    Args:
        date_str: The date string to convert.

    Returns:
        The unix timestamp corresponding to the date string.

    If the date string cannot be parsed as a valid date format, returns the current unix timestamp and prints a warning.
    """
    try: 
        date_obj = arrow.get(date_str)
        return int(date_obj.timestamp())
    except arrow.parser.ParserError:
        print(f"Warning: {date_str} could not be parsed as a valid date format. Returning current unix timestamp.")
        return int(arrow.now().timestamp())
    



def to_datestr(datenum: str):
    """
    Convert a unix timestamp (seconds since epoch) to a date string.
    """
    date_time_obj = datetime.fromtimestamp(float(datenum))
    date_str = date_time_obj.strftime('%Y-%m-%d')
    return date_str

