"""Row-cap fetching and cost/budget guards."""

import math


class RowCapExceeded(Exception):
    pass


def fetch_capped(cursor, sql, params=(), max_rows=100):
    """Fetch at most ``max_rows`` rows, without rewriting the query.

    The query is executed exactly as given -- no LIMIT is appended or
    injected. ``fetchmany(max_rows + 1)`` detects overflow: if more rows
    exist than the cap allows, the call fails loudly instead of
    silently truncating.
    """
    if max_rows < 0:
        raise ValueError("max_rows must not be negative")
    rows = cursor.execute(sql, params).fetchmany(max_rows + 1)
    if len(rows) > max_rows:
        raise RowCapExceeded(
            f"query returned more than {max_rows} rows; refusing to truncate"
        )
    return rows
