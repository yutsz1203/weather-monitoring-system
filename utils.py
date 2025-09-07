import contextlib
import time
from datetime import datetime, timedelta
from rich.errors import NotRenderableError
from rich.progress import Progress
from rich.console import Console


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

def countdown(interval):
    console = Console()
    now = datetime.now()
    minute = (now.minute // interval) * interval
    next_quarter = minute + interval
    if next_quarter == 60:
        next_time = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
    else:
        next_time = now.replace(minute=next_quarter, second=0, microsecond=0)
    seconds_left = int((next_time - now).total_seconds())
    minutes_left = seconds_left // 60
    if minutes_left <= 5:
        color = "green"
    elif minutes_left <= 10:
        color = "yellow"
    else:
        color = "red"
    console.log(f"[{color}]{minutes_left}[/] minutes and [{color}]{seconds_left - minutes_left * 60}[/] seconds until next fetch")
    with Progress() as progress:
        task = progress.add_task("Waiting", total=seconds_left)
        for _ in range(seconds_left):
            time.sleep(1)
            progress.update(task, advance=1)