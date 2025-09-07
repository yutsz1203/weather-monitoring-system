import contextlib
import math
import time
from datetime import datetime, timedelta

from rich.console import Console
from rich.errors import NotRenderableError
from rich.progress import Progress

HK_LAT = 22.302711
HK_LONG = 114.177216

def get_distance_from_lat_lon_km(lat, lon):
    """
    Calculate the great-circle distance between two points on the Earth 
    using the Haversine formula.
    
    Parameters:
    lat1, lon1: Latitude and longitude of first point in degrees
    lat2, lon2: Latitude and longitude of second point in degrees
    
    Returns:
    Distance between the points in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    # Convert degrees to radians
    d_lat = math.radians(HK_LAT - lat)
    d_lon = math.radians(HK_LONG - lon)
    
    # Haversine formula
    a = (math.sin(d_lat/2) * math.sin(d_lat/2) +
         math.cos(math.radians(HK_LAT)) * math.cos(math.radians(lat)) *
         math.sin(d_lon/2) * math.sin(d_lon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c  # Distance in km
    return distance


def rich_display_dataframe(df, title="Dataframe") -> None:
    """Display dataframe as table using rich library.
    Args:
        df (pd.DataFrame): dataframe to display
        title (str, optional): title of the table. Defaults to "Dataframe".
    Raises:
        NotRenderableError: if dataframe cannot be rendered
    Returns:
        rich.table.Table: rich table
    """
    from rich import print
    from rich.table import Table

    # ensure dataframe contains only string values
    df = df.astype(str)

    table = Table(title=title)
    for col in df.columns:
        table.add_column(col)
    for row in df.values:
        with contextlib.suppress(NotRenderableError):
            table.add_row(*row)
    print(table)

def countdown(interval, type="info"):
    console = Console()
    now = datetime.now()
    if type == "info":
        minute = (now.minute // interval) * interval
        next_quarter = minute + interval
        if next_quarter == 60:
            next_time = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
        else:
            next_time = now.replace(minute=next_quarter, second=0, microsecond=0)
    elif type == "TCSGNL":
        next_time = (now.replace(minute=46, second=0, microsecond=0)) if now.minute < 46 else (now.replace(minute=46, second=0, microsecond=0) + timedelta(hours=1))
        
    seconds_left = int((next_time - now).total_seconds())
    minutes_left = seconds_left // 60
    if minutes_left <= 5:
        color = "green"
    elif minutes_left <= 10:
        color = "yellow"
    else:
        color = "red"
    if minutes_left == 60:
        console.log(f"[{color}]1[/] hour until next fetch")
    else:
        console.log(f"[{color}]{minutes_left}[/] minutes and [{color}]{seconds_left - minutes_left * 60}[/] seconds until next fetch")

    with Progress() as progress:
        task = progress.add_task("Waiting", total=seconds_left)
        for _ in range(seconds_left):
            time.sleep(1)
            progress.update(task, advance=1)