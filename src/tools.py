from datetime import datetime
from typing import Dict

def get_current_datetime() -> Dict[str, str]:
    """
    Returns current date and time information
    """
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "month_day": now.strftime("%m-%d")
    }

def get_day_of_week(date_str: str) -> Dict[str, str]:
    """
    Returns the day of week for a given date string.
    Args:
        date_str (str): Date string in format 'YYYY-MM-DD'
    Returns:
        Dict with date and day of week information
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return {
            "date": date_str,
            "day_of_week": date_obj.strftime("%A")
        }
    except ValueError:
        return {
            "date": date_str,
            "error": "Invalid date format. Please use YYYY-MM-DD format."
        }

