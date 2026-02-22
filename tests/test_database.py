import sqlite3

import pytest

from bear import database


def connect() -> sqlite3.Connection:
    return sqlite3.connect(":memory:")


@pytest.fixture
def conn():
    conn = connect()
    conn.execute(
        """
        CREATE TABLE ZSFNOTE (
            Z_PK INTEGER PRIMARY KEY,
            ZTITLE VARCHAR,
            ZUNIQUEIDENTIFIER VARCHAR,
            ZCREATIONDATE TIMESTAMP,
            ZMODIFICATIONDATE TIMESTAMP,
            ZTRASHED INTEGER,
            ZPERMANENTLYDELETED INTEGER,
            ZTEXT VARCHAR
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE ZSFNOTETAG ( 
                Z_PK INTEGER PRIMARY KEY, 
                ZTITLE VARCHAR
            )
        """
    )
    conn.execute(
        """
        CREATE TABLE Z_5TAGS ( 
            Z_5NOTES INTEGER,
            Z_13TAGS INTEGER, 
            PRIMARY KEY (Z_5NOTES, Z_13TAGS) 
            )
        """
    )

    conn.executemany(
        "INSERT INTO ZSFNOTE VALUES (?, ?, ?, ?, ?, ?, ?,?)",
        [
            (1, "Note 1", "uuid-1", 100, 200, 0, 0, ""),
            (2, "Note 2", "uuid-2", 200, 300, 0, 0, ""),
            (3, "Note 3", "uuid-3", 300, 400, 0, 0, ""),
            (4, "Note 4", "uuid-4", 400, 500, 1, 0, ""),
            (5, "Note 5", "uuid-5", 400, 500, 0, 0, ""),
            (6, "Note 5", "uuid-6", 400, 500, 0, 0, ""),
        ],
    )
    conn.executemany(
        "INSERT INTO ZSFNOTETAG VALUES (?, ?)",
        [
            (1, "tag_1"),
            (2, "tag_2"),
        ],
    )
    conn.executemany(
        "INSERT INTO Z_5TAGS VALUES (?, ?)",
        [
            (1, 1),
            (2, 2),
            (3, 1),
            (6, 1),
        ],
    )

    conn.commit()
    yield conn
    conn.close()


def test_get_notes(conn):
    notes = database.get_notes(conn)
    assert len(notes) == 5
    assert notes[0].title == "Note 1"
    assert notes[0].identifier == "uuid-1"


def test_get_notes_excludes_trashed(conn):
    notes = database.get_notes(conn)
    assert not any(note.title == "Note 4" for note in notes)
    assert any(note.title == "Note 1" for note in notes)


def test_get_tags(conn):
    tags = database.get_tags(conn)
    assert len(tags) == 2
    assert tags[0].title == "tag_1"
    assert tags[1].title == "tag_2"


def test_search_notes(conn):
    notes = database.search_notes(conn, "2")
    assert len(notes) == 1
    assert notes[0].title == "Note 2"


def test_get_orphaned_notes(conn):
    notes = database.get_orphaned_notes(conn)
    assert len(notes) == 1
    assert notes[0].title == "Note 5"


def test_get_duplicate_titles(conn):
    dups = database.get_duplicate_titles(conn)
    assert len(dups) == 1
    assert dups["Note 5"] == 2
