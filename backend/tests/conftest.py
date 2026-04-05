import sqlite3
from collections.abc import Generator

import pytest


@pytest.fixture
def sqlite_connection() -> Generator[sqlite3.Connection, None, None]:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()
