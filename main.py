from bear import database, writer


def main() -> None:
    print("Hello from bear!")
    with database.connect() as conn:
        notes = database.get_notes(conn)
        tags = database.get_tags(conn)
        for note in notes:
            print(f"{note.title} {note.identifier}")

        for tag in tags:
            print(f"{tag.title} {tag.pk}")

        print("search_notes")
        term = "Port Authority"
        notes = database.search_notes(conn, term)
        for note in notes:
            print(
                f"{note.title} {note.identifier} {note.creation_date} {note.modification_date}"
            )

        print("get_notes_with_tags")
        notes = database.get_notes_with_tags(conn)
        for note in notes:
            tags = [tag.title for tag in note.tags]
            print(f"{note.title} {note.identifier} tags:{tags}")

        stats = database.get_stats(conn)
        print(stats)

        print("get_orphaned_notes")
        notes = database.get_orphaned_notes(conn)
        for note in notes:
            print(f"{note.title} {note.identifier}")

        print("get_duplicate_titles")
        dups = database.get_duplicate_titles(conn)
        print(f"dups count {len(dups)}")
        for title, count in list(dups.items())[:10]:
            print(f"  {count}x  {title}")

        writer.create_note("[TEST] My First Python Note")

        term = "kuku"
        notes = database.search_notes(conn, term, limit=1)
        writer.open_note(notes[0].identifier)

        print("search_notes")
        term = "[TEST]"
        notes = database.search_notes(conn, term)
        for note in notes:
            print(f"{note.title} {note.identifier}")
            writer.trash_note(note.identifier)

        tag = ".journal/2025/01/20"
        notes = database.search_notes_by_tag(conn, tag, limit=1)
        note = notes[0]
        print(f"{note.title} {note.identifier}")


if __name__ == "__main__":
    main()
