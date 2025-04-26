import requests
import re as _re
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional

DATABASE_FILE = "movies.db"

def _get_movie_details(movie_url: str) -> tuple[str, dict]:
    """
    Internal helper function to fetch movie details from ČSFD.cz.
    Args:
        movie_url (str): Direct URL to the movie page on ČSFD.cz.
    Returns:
        tuple: (display_text, movie_data) where movie_data contains structured information
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'cs-CZ,cs;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }

    print(f"DEBUG: Fetching movie details from: {movie_url}")
    try:
        # Get movie details page
        movie_resp = requests.get(movie_url, headers=headers, timeout=10)
        movie_resp.raise_for_status()
        movie_soup = BeautifulSoup(movie_resp.text, 'html.parser')
        
        # Get movie name from the page title
        movie_name_elem = movie_soup.select_one('h1')
        movie_name = movie_name_elem.text.strip() if movie_name_elem else "Unknown"
        
        # Extract genre - try multiple possible selectors
        genre_elem = (
            movie_soup.select_one('div.genres ul.genres-list') or
            movie_soup.select_one('div.genres') or
            movie_soup.select_one('p.genre')
        )
        genre_val = genre_elem.text.strip() if genre_elem else "Unknown"
        
        # Extract rating - try multiple possible selectors
        rating_elem = (
            movie_soup.select_one('div.film-rating-average') or
            movie_soup.select_one('div.rating-average') or
            movie_soup.select_one('h2.rating')
        )
        rating_text = rating_elem.text.strip() if rating_elem else "Unknown"
        # Remove any existing % sign and add our own
        rating_val = rating_text.replace('%', '') + "%" if rating_text != "Unknown" else "Unknown"
        
        display_text = f"Movie Information:\nName: {movie_name}\nGenre: {genre_val}\nRating: {rating_val}\nURL: {movie_url}"
        print(f"DEBUG: Returning movie info: Name={movie_name}, Genre={genre_val}, Rating={rating_val}, URL={movie_url}")
        
        movie_data = {
            "name": movie_name,
            "genre": genre_val,
            "rating": rating_val,
            "url": movie_url
        }
        
        return display_text, movie_data
        
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Error during request: {e}")
        return f"Error fetching movie information: {str(e)}", None
    except Exception as e:
        print(f"DEBUG: Error processing response: {e}")
        print(f"DEBUG: Full error: {str(e)}")
        return f"Error processing movie information: {str(e)}", None

def get_movie_information(movie_url: str) -> str:
    """
    Fetch genre, rating, and other information for a movie from ČSFD.cz using its URL.
    Args:
        movie_url (str): Direct URL to the movie page on ČSFD.cz.
    Returns:
        str: A formatted string containing movie information, or error message if fetching fails.
    """
    display_text, movie_data = _get_movie_details(movie_url)
    return display_text

def read_name_days() -> Dict[str, List[str]]:
    """
    Reads name days from the CSV file and returns a dictionary where
    key is date in format 'MM-DD' and value is list of names
    """
    name_days = {}
    try:
        with open('data/name_days.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header if exists
            for row in reader:
                date = row[0]  # Assuming date is in first column
                names = [name.strip() for name in row[1:] if name.strip()]  # Get all non-empty names
                name_days[date] = names
        return name_days
    except FileNotFoundError:
        return {}

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

