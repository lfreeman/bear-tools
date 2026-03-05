import json
import sys
from dataclasses import asdict
from datetime import datetime, timedelta

import questionary
import rich
import typer
from questionary import Choice
from rich.table import Table

from bear import database, templates, writer

from .models import Note, OutputFormat, Period

app = typer.Typer()


@app.command()
def stats(output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o")):
    """Show database statistics"""
    with database.connect() as conn:
        stats = database.get_stats(conn)
        if output == OutputFormat.TABLE:
            table = Table()
            table.add_column("Metric")
            table.add_column("Count")
            table.add_row("Total notes", str(stats.total_notes))
            table.add_row("Trashed", str(stats.trashed_notes))
            table.add_row("Tags", str(stats.total_tags))
            table.add_row("Orphaned", str(stats.orphaned_notes))
            table.add_row("Duplicates", str(stats.dups_notes))
            rich.print(table)
        else:
            print(json.dumps(asdict(stats), default=str))


@app.command()
def search(
    term: str,
    limit: int = 20,
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o"),
):
    """Search notes by title or content."""
    with database.connect() as conn:
        notes = database.search_notes(conn, term, limit)
        display_notes(notes, output)


@app.command()
def orphaned(limit: int = 20, output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o")):
    """List orphaned notes"""
    with database.connect() as conn:
        notes = database.get_orphaned_notes(conn, limit)
        display_notes(notes, output)


def display_notes(notes: list[Note], output: OutputFormat = OutputFormat.TABLE):
    if output == OutputFormat.TABLE:
        if sys.stdin.isatty() and notes:
            max_len = max(len(note.title[:70]) for note in notes)
            choices = [
                Choice(
                    title=f"{note.title[:70]:<{max_len}}  ({note.modification_date.strftime('%Y-%m-%d %H:%M')})",
                    value=note.identifier,
                )
                for note in notes
            ]
            choices.append(Choice(title="Quit", value="quit"))
            while True:
                selected = questionary.select("Open note:", choices=choices).ask()
                if not selected or selected == "quit":
                    break
                writer.open_note(selected)

        else:
            table = Table()
            table.add_column("Title")
            table.add_column("Identifier")
            table.add_column("Created")
            table.add_column("Modified")
            for note in notes:
                table.add_row(
                    note.title,
                    note.identifier,
                    note.creation_date.strftime("%Y-%m-%d %H:%M"),
                    note.modification_date.strftime("%Y-%m-%d %H:%M"),
                )
            rich.print(table)
    else:
        print(json.dumps([asdict(note) for note in notes], default=str))


@app.command()
def duplicates(
    limit: int = 20,
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o"),
):
    """List duplicates"""
    with database.connect() as conn:
        dups = database.get_duplicate_titles(conn, limit)

        if output == OutputFormat.TABLE:
            table = Table()
            table.add_column("Title")
            table.add_column("Count")
            for title, count in dups.items():
                table.add_row(title, str(count))
            rich.print(table)
        else:
            print(json.dumps(dups))


@app.command()
def create(title: str, text: str = "", tags: list[str] | None = None):
    """Create note"""
    writer.create_note(title, text, tags)


@app.command()
def journal():
    """Journal"""
    title, text, tags = templates.daily_journal()
    with database.connect() as conn:
        notes = database.search_notes_by_tag(conn, tags[0], limit=1)
        if notes:
            writer.open_note(notes[0].identifier)
        else:
            writer.create_note(title, text)  # no tags param — tag is in the text


@app.command()
def dedup(yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")):
    """dedup"""
    with database.connect() as conn:
        groups = database.get_content_duplicates(conn)
        for title, notes in groups.items():
            if yes or typer.confirm(f"Delete {len(notes) - 1} duplicates of '{title}'?"):
                for note in notes[1:]:
                    writer.trash_note(note.identifier)


@app.command()
def summary(
    period: Period = typer.Option(Period.DAY, "--period", "-p"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o"),
):
    """Summary"""
    with database.connect() as conn:
        if period == Period.DAY:
            since = datetime.now() - timedelta(days=1)
        else:
            since = datetime.now() - timedelta(weeks=1)

        notes = database.get_recent_notes(conn, since)
        display_notes(notes, output)


@app.command()
def import_file(file_path: str):
    """create note from file"""
    writer.import_file(file_path)
