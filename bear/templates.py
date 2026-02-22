from datetime import date


def daily_journal() -> tuple[str, str, list[str]]:
    today = date.today()
    title = today.strftime("%b %d, %Y")
    # text = "## Highlights\n- \n\n## Tasks\n- [ ] \n\n## Notes\n- \n\n"
    tag = f".journal/{today.strftime('%Y/%m/%d')}"
    text = f"## Highlights\n- \n\n## Tasks\n- [ ] \n\n## Notes\n- \n\n#{tag}"

    return (title, text, [tag])
