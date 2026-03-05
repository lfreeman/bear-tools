import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from .models import Note, Order, SortBy, Stats, Tag

APPLE_EPOCH = datetime(2001, 1, 1)


def apple_timestamp_to_datetime(timestamp: float) -> datetime:
    return APPLE_EPOCH + timedelta(seconds=timestamp)


def datetime_to_apple_timestamp(dt: datetime) -> float:
    return (dt - APPLE_EPOCH).total_seconds()


def get_db_path() -> Path:
    return Path(
        "~/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite"
    ).expanduser()


def get_notes(conn: sqlite3.Connection, limit: int = 20) -> list[Note]:
    cursor = conn.execute(
        "SELECT ZTITLE, ZUNIQUEIDENTIFIER ,ZCREATIONDATE, ZMODIFICATIONDATE FROM ZSFNOTE  WHERE ZTRASHED= 0 AND  ZPERMANENTLYDELETED=0 limit ?",
        (limit,),
    )
    rows = cursor.fetchall()
    return [
        Note(
            title=row[0],
            identifier=row[1],
            creation_date=apple_timestamp_to_datetime(row[2]),
            modification_date=apple_timestamp_to_datetime(row[3]),
        )
        for row in rows
    ]


def get_tags(conn: sqlite3.Connection, limit: int = 20) -> list[Tag]:
    cursor = conn.execute("SELECT Z_PK, ZTITLE FROM ZSFNOTETAG limit ?", (limit,))
    rows = cursor.fetchall()
    return [Tag(title=row[1], pk=row[0]) for row in rows]


def connect() -> sqlite3.Connection:
    path = get_db_path()
    return sqlite3.connect(path)


def search_notes(
    conn: sqlite3.Connection,
    term: str,
    limit: int = 20,
    sort_by: SortBy = SortBy.CREATED,
    order: Order = Order.DESC,
) -> list[Note]:
    cursor = conn.execute(
        f"""
        SELECT ZTITLE, ZUNIQUEIDENTIFIER , ZCREATIONDATE, ZMODIFICATIONDATE
        FROM ZSFNOTE  
        WHERE ZTRASHED= 0 AND  ZPERMANENTLYDELETED=0 AND (ZTITLE like :term OR ZTEXT like :term )   
        ORDER BY {sort_by.value} {order.value}
        LIMIT :limit
        """,
        {"term": f"%{term}%", "limit": limit},
    )
    rows = cursor.fetchall()
    return [
        Note(
            title=row[0],
            identifier=row[1],
            creation_date=apple_timestamp_to_datetime(row[2]),
            modification_date=apple_timestamp_to_datetime(row[3]),
        )
        for row in rows
    ]


def get_notes_with_tags(conn: sqlite3.Connection, limit: int = 20) -> list[Note]:
    cursor = conn.execute(
        """
        SELECT n.ZTITLE, n.ZUNIQUEIDENTIFIER, t.Z_PK, t.ZTITLE,
        n.ZCREATIONDATE, n.ZMODIFICATIONDATE
        FROM ZSFNOTE n
        JOIN Z_5TAGS jt ON n.Z_PK = jt.Z_5NOTES
        JOIN ZSFNOTETAG t ON jt.Z_13TAGS = t.Z_PK
        WHERE n.ZTRASHED = 0 AND n.ZPERMANENTLYDELETED = 0
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    notes = {}
    for title, identifier, tag_pk, tag_title, creation_date, modification_date in rows:
        if identifier not in notes:
            notes[identifier] = Note(
                title=title,
                identifier=identifier,
                creation_date=apple_timestamp_to_datetime(creation_date),
                modification_date=apple_timestamp_to_datetime(modification_date),
            )
        notes[identifier].tags.append(Tag(title=tag_title, pk=tag_pk))

    return list(notes.values())


def get_stats(conn: sqlite3.Connection) -> Stats:

    cursor = conn.execute("SELECT COUNT(*) FROM ZSFNOTE WHERE ZTRASHED=0 AND ZPERMANENTLYDELETED=0")
    total_notes = cursor.fetchone()[0]

    cursor = conn.execute("SELECT COUNT(*) FROM ZSFNOTE WHERE ZTRASHED=1")
    trashed_notes = cursor.fetchone()[0]

    cursor = conn.execute("SELECT COUNT(*) FROM ZSFNOTETAG")
    total_tags = cursor.fetchone()[0]

    cursor = conn.execute(
        """
        SELECT count(*) FROM (
        SELECT ZTEXT
        FROM ZSFNOTE
        WHERE ZTRASHED=0 AND ZPERMANENTLYDELETED=0
        AND ZTEXT IS NOT NULL AND ZTEXT != ''
        AND ZTITLE IS NOT NULL AND ZTITLE != ''
        GROUP BY ZTEXT
        HAVING COUNT(ZTEXT) > 1
       )
       """
    )
    dups_notes = cursor.fetchone()[0]

    cursor = conn.execute(
        """
         SELECT count(*)
         from ZSFNOTE n                                                                                                                                                                                            
         LEFT JOIN Z_5TAGS jt ON n.Z_PK = jt.Z_5NOTES                                                                                                                                                                              
         WHERE jt.Z_5NOTES IS NULL AND n.ZTRASHED=0 AND n.ZPERMANENTLYDELETED=0 
        """
    )
    orphaned_notes = cursor.fetchone()[0]

    return Stats(
        total_notes=total_notes,
        trashed_notes=trashed_notes,
        total_tags=total_tags,
        orphaned_notes=orphaned_notes,
        dups_notes=dups_notes,
    )


def get_orphaned_notes(conn: sqlite3.Connection, limit: int = 20) -> list[Note]:
    cursor = conn.execute(
        """
         SELECT n.ZTITLE, n.ZUNIQUEIDENTIFIER ,n.ZCREATIONDATE, n.ZMODIFICATIONDATE
         from ZSFNOTE n                                                                                                                                                                                            
         LEFT JOIN Z_5TAGS jt ON n.Z_PK = jt.Z_5NOTES                                                                                                                                                                              
         WHERE jt.Z_5NOTES IS NULL AND n.ZTRASHED=0 AND n.ZPERMANENTLYDELETED=0 
         LIMIT :limit
         """,
        {"limit": limit},
    )
    rows = cursor.fetchall()
    return [
        Note(
            title=row[0],
            identifier=row[1],
            creation_date=apple_timestamp_to_datetime(row[2]),
            modification_date=apple_timestamp_to_datetime(row[3]),
        )
        for row in rows
    ]


def get_duplicate_titles(conn: sqlite3.Connection, limit: int = 20) -> dict[str, int]:
    cursor = conn.execute(
        """
            SELECT ZTITLE, COUNT(*) as count
            FROM ZSFNOTE
            WHERE ZTRASHED=0 AND ZPERMANENTLYDELETED=0
            GROUP BY ZTITLE
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT :limit
        """,
        {"limit": limit},
    )
    rows = cursor.fetchall()
    return {title: count for title, count in rows}


def search_notes_by_tag(conn: sqlite3.Connection, tag: str, limit: int = 20):
    cursor = conn.execute(
        """
        SELECT n.ZTITLE, n.ZUNIQUEIDENTIFIER, t.Z_PK, t.ZTITLE,
        n.ZCREATIONDATE, n.ZMODIFICATIONDATE
        FROM ZSFNOTE n
        JOIN Z_5TAGS jt ON n.Z_PK = jt.Z_5NOTES
        JOIN ZSFNOTETAG t ON jt.Z_13TAGS = t.Z_PK
        WHERE n.ZTRASHED = 0 
        AND n.ZPERMANENTLYDELETED = 0
        AND t.ZTITLE = :tag
        LIMIT :limit
        """,
        {"tag": tag, "limit": limit},
    )
    rows = cursor.fetchall()
    notes = {}
    for title, identifier, tag_pk, tag_title, creation_date, modification_date in rows:
        if identifier not in notes:
            notes[identifier] = Note(
                title=title,
                identifier=identifier,
                creation_date=apple_timestamp_to_datetime(creation_date),
                modification_date=apple_timestamp_to_datetime(modification_date),
            )
        notes[identifier].tags.append(Tag(title=tag_title, pk=tag_pk))

    return list(notes.values())


def get_content_duplicates(conn: sqlite3.Connection) -> dict[str, list[Note]]:
    cursor = conn.execute(
        """
        SELECT ZTITLE, ZUNIQUEIDENTIFIER ,ZCREATIONDATE, ZMODIFICATIONDATE
        FROM ZSFNOTE WHERE ZTEXT IN
		(
            SELECT ZTEXT
            FROM ZSFNOTE
            WHERE ZTRASHED=0 AND ZPERMANENTLYDELETED=0
            AND ZTEXT IS NOT NULL AND ZTEXT != ''
            AND ZTITLE IS NOT NULL AND ZTITLE != ''
            GROUP BY ZTEXT
            HAVING COUNT(ZTEXT) > 1
            ORDER BY COUNT(*) DESC
        ) 
        AND  ZTRASHED=0 AND ZPERMANENTLYDELETED=0
        ORDER BY ZTITLE ,ZMODIFICATIONDATE DESC
        """
    )
    rows = cursor.fetchall()
    notes = {}
    for title, identifier, creation_date, modification_date in rows:
        if title not in notes:
            notes[title] = []
        notes[title].append(
            Note(
                title=title,
                identifier=identifier,
                creation_date=apple_timestamp_to_datetime(creation_date),
                modification_date=apple_timestamp_to_datetime(modification_date),
            )
        )
    return notes


def get_recent_notes(conn: sqlite3.Connection, since: datetime) -> list[Note]:
    date = datetime_to_apple_timestamp(since)
    cursor = conn.execute(
        """
        SELECT ZTITLE, ZUNIQUEIDENTIFIER ,ZCREATIONDATE, ZMODIFICATIONDATE
        FROM ZSFNOTE  WHERE ZTRASHED= 0 AND  ZPERMANENTLYDELETED=0 AND ZMODIFICATIONDATE >= :date
        ORDER BY ZMODIFICATIONDATE DESC
        """,
        {"date": date},
    )
    rows = cursor.fetchall()
    return [
        Note(
            title=row[0],
            identifier=row[1],
            creation_date=apple_timestamp_to_datetime(row[2]),
            modification_date=apple_timestamp_to_datetime(row[3]),
        )
        for row in rows
    ]


def get_note(conn: sqlite3.Connection, identifier: str) -> Note:
    """Get note"""
    cursor = conn.execute(
        """
        SELECT ZTITLE, ZUNIQUEIDENTIFIER, ZCREATIONDATE, ZMODIFICATIONDATE, ZTEXT 
        FROM ZSFNOTE WHERE ZUNIQUEIDENTIFIER = :identifier
        """,
        {"identifier": identifier},
    )
    row = cursor.fetchone()

    return Note(
        title=row[0],
        identifier=row[1],
        creation_date=apple_timestamp_to_datetime(row[2]),
        modification_date=apple_timestamp_to_datetime(row[3]),
        text=row[4],
    )
