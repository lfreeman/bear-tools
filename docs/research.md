# Bear Notes Programmatic Access — Research

Collected Feb 2025. Reference material for building Python tooling around Bear.app.

## Bear SQLite Database

**Location**: `~/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite`

Bear uses Core Data + SQLite. Tables prefixed with `Z`, columns with `Z` (Apple Core Data convention).

**Timestamps**: Core Data epoch — seconds since **2001-01-01** (not Unix 1970).
SQL conversion: `datetime(ZCREATIONDATE, 'unixepoch', '+31 years')`

### Schema (key tables)

**ZSFNOTE** — Notes
| Column | Type | Description |
|---|---|---|
| Z_PK | INTEGER | Primary key |
| ZTITLE | VARCHAR | Note title |
| ZSUBTITLE | VARCHAR | First line / subtitle |
| ZTEXT | VARCHAR | Full note content (Bear markdown) |
| ZUNIQUEIDENTIFIER | VARCHAR | UUID used by x-callback-url |
| ZTRASHED | INTEGER | 1 if in trash |
| ZARCHIVED | INTEGER | 1 if archived |
| ZPINNED | INTEGER | 1 if pinned |
| ZENCRYPTED | INTEGER | 1 if encrypted (ZTEXT will be empty) |
| ZLOCKED | INTEGER | 1 if locked |
| ZHASFILES | INTEGER | Has attachments |
| ZHASIMAGES | INTEGER | Has images |
| ZHASSOURCECODE | INTEGER | Has code blocks |
| ZTODOCOMPLETED | INTEGER | Count of completed todos |
| ZTODOINCOMPLETED | INTEGER | Count of incomplete todos |
| ZCREATIONDATE | TIMESTAMP | Core Data epoch |
| ZMODIFICATIONDATE | TIMESTAMP | Core Data epoch |
| ZPERMANENTLYDELETED | INTEGER | 1 if permanently deleted |
| ZVERSION | INTEGER | Version counter |
| ZLASTEDITINGDEVICE | VARCHAR | Device name |
| ZPASSWORD | INTEGER | FK to ZSFPASSWORD |
| ZSERVERDATA | INTEGER | FK to ZSFNOTESERVERDATA |

**ZSFNOTETAG** — Tags
| Column | Type | Description |
|---|---|---|
| Z_PK | INTEGER | Primary key |
| ZTITLE | VARCHAR | Tag name (e.g. "work/projects") |
| ZPINNED | INTEGER | 1 if pinned in sidebar |
| ZUNIQUEIDENTIFIER | VARCHAR | UUID |
| ZMODIFICATIONDATE | TIMESTAMP | Core Data epoch |

**Z_5TAGS** — Note-to-Tag junction table
| Column | Type | Description |
|---|---|---|
| Z_5NOTES | INTEGER | FK to ZSFNOTE.Z_PK |
| Z_13TAGS | INTEGER | FK to ZSFNOTETAG.Z_PK |

**ZSFNOTEFILE** — Attachments
| Column | Type | Description |
|---|---|---|
| Z_PK | INTEGER | Primary key |
| ZNOTE | INTEGER | FK to ZSFNOTE.Z_PK |
| ZFILENAME | VARCHAR | Original filename |
| ZFILESIZE | INTEGER | Size in bytes |
| ZNORMALIZEDFILEEXTENSION | VARCHAR | e.g. "png", "pdf" |
| ZWIDTH / ZHEIGHT | INTEGER | Image dimensions |
| ZCREATIONDATE | TIMESTAMP | Core Data epoch |
| ZUNIQUEIDENTIFIER | VARCHAR | UUID |

**ZSFNOTEBACKLINK** — Links between notes
| Column | Type | Description |
|---|---|---|
| Z_PK | INTEGER | Primary key |
| ZLINKEDBY | INTEGER | FK to ZSFNOTE.Z_PK (source note) |
| ZLINKINGTO | INTEGER | FK to ZSFNOTE.Z_PK (target note) |
| ZTITLE | VARCHAR | Link text |
| ZLOCATION | INTEGER | Position in source note |

### Other tables (less commonly used)
- `ZSFPASSWORD` — encryption passwords
- `ZSFNOTESERVERDATA` / `ZSFNOTEFILESERVERDATA` / `ZSFSERVERMETADATA` — iCloud sync
- `ZSFCHANGE` / `ZSFCHANGEITEM` / `ZSFEXTERNALCHANGES` / `ZSFINTERNALCHANGES` — sync change tracking
- `Z_5PINNEDINTAGS` — pinned notes within specific tags
- `Z_METADATA` / `Z_MODELCACHE` / `Z_PRIMARYKEY` — Core Data internals

### Current database stats (this machine)
- 6,234 active notes
- 767 tags
- 6,051 note-tag relationships

---

## x-callback-url API

Docs: https://bear.app/faq/x-callback-url-scheme-documentation/
URL builder: https://bear.app/xurl/create/
API v2.0: https://guides.bear-lab.com/api/2.0/doc/

**API token**: Bear → Help → Advanced → API Token → Copy Token (required for read actions that return data)

### Actions

| Action | Purpose | Needs token? | Returns data? |
|---|---|---|---|
| `/open-note` | Open note by id or title | For `selected` param | note text, id, title, tags, dates |
| `/create` | Create new note | No | identifier, title |
| `/add-text` | Append/prepend text to note | For `selected` param | note text, title |
| `/add-file` | Attach file to note | For `selected` param | note text |
| `/tags` | List all tags | Yes | tags array |
| `/open-tag` | Show notes with tag | Optional | notes array |
| `/rename-tag` | Rename tag | No | — |
| `/delete-tag` | Delete tag | No | — |
| `/trash` | Trash a note | No | — |
| `/archive` | Archive a note | No | — |
| `/untagged` | Show untagged notes | Optional | notes array |
| `/todo` | Show notes with todos | Optional | notes array |
| `/today` | Show today's notes | Optional | notes array |
| `/locked` | Show locked sidebar | No | — |
| `/search` | Search notes | Optional | notes array |
| `/grab-url` | Create note from web URL | No | identifier, title |

### Calling from Python
- **Writes (fire-and-forget)**: `subprocess.run(["open", "bear://x-callback-url/create?title=..."])`
- **Reads (need response)**: Requires `xcall` utility or similar callback receiver
- **Key limitation**: x-callback-url is app-to-app; getting responses back to a script is non-trivial

---

## Community Projects

### MCP Servers (AI Integration)

| Project | Tech | Access | Features |
|---|---|---|---|
| [bejaminjones/bear-notes-mcp](https://github.com/bejaminjones/bear-notes-mcp) | TypeScript | Hybrid (SQLite read + xcallback write) | 32 tools, 384 tests, service-oriented architecture, analytics |
| [vasylenko/claude-desktop-extension-bear-notes](https://github.com/vasylenko/claude-desktop-extension-bear-notes) | TypeScript | Hybrid + OCR support | Claude Desktop extension, fully local |
| [ruanodendaal/bear-mcp-server](https://github.com/ruanodendaal/bear-mcp-server) | Node.js + transformers.js | SQLite read-only | Semantic search with all-MiniLM-L6-v2 embeddings (384-dim), RAG retrieval |
| [netologist/mcp-bear-notes](https://github.com/netologist/mcp-bear-notes) | — | SQLite read-only | Basic MCP server |
| [akseyh/bear-mcp-server](https://github.com/akseyh/bear-mcp-server) | — | SQLite | MCP integration |
| [bart6114/my-bear-mcp-server](https://github.com/bart6114/my-bear-mcp-server) | — | SQLite read-only | Read-only access for AI assistants |
| mreider/bear-sql (on [LobeHub](https://lobehub.com/mcp/mreider-bear-sql)) | — | SQLite | Raw SQL execution against Bear DB |

### Export & Backup

| Project | Tech | What it does |
|---|---|---|
| [andymatuschak/Bear-Markdown-Export](https://github.com/andymatuschak/Bear-Markdown-Export) | Python | Bidirectional sync to markdown/textbundles, tag-based folders, image handling, cron-schedulable |
| [mivok/bear_backup](https://github.com/mivok/bear_backup) | Python | Dumps notes to .bearnote files (re-importable) |
| [seancdavis/bear-to-markdown](https://github.com/seancdavis/bear-to-markdown) | Node.js | Export to markdown files |
| [greven/bear-export](https://github.com/greven/bear-export) | Python | Simple unidirectional markdown export |

### Graph Visualization

| Project | Tech | What it does |
|---|---|---|
| [codeKgu/Bear-Graph](https://github.com/codeKgu/Bear-Graph) | Python, Streamlit | Interactive dashboard — notes as graph nodes, links and tags as edges |
| [rberenguel/bear-note-graph](https://github.com/rberenguel/bear-note-graph) | Python, Graphviz | CLI graph generation, on PyPI |
| [mgrabka/bear-graph](https://github.com/mgrabka/bear-graph) | — | Graph view of notes |

### Backlinks & Zettelkasten

| Project | Tech | What it does |
|---|---|---|
| [cdzombak/bear-backlinks](https://github.com/cdzombak/bear-backlinks) | Python + xcall | Auto-generate `## Backlinks` sections in notes, timestamped backups |
| [dlleigh/bear-backlinks](https://github.com/dlleigh/bear-backlinks) | Python | Fork of above |
| [cglacet/bear](https://github.com/cglacet/bear) | — | Back-references via SQLite |

### CLI Tools & Libraries

| Project | Tech | What it does |
|---|---|---|
| [redspider/pybear](https://github.com/redspider/pybear) | Python | Simple SQLite reader — `Bear()`, `notes()`, `tags()`. Dormant. |
| [sloansparger/bear](https://github.com/sloansparger/bear) | Node.js/TypeScript | Unofficial CLI via x-callback-url |
| [a5huynh/cub-cli](https://github.com/a5huynh/cub-cli) | Rust | `cub ls`, `cub show [ID]` — fast CLI, available via Homebrew |
| [jakeswenson/bear-query](https://github.com/jakeswenson/bear-query) | Rust | Library on docs.rs for querying Bear SQLite |
| [ValentinWalter/Honey](https://github.com/ValentinWalter/Honey) | Swift | Swift API for Bear |
| [anjiro/bearutils](https://github.com/anjiro/bearutils) | Python | Note processing utilities |

### Publishing / CMS

| Project | Tech | What it does |
|---|---|---|
| [crisfeim/cli-bearpublish](https://github.com/crisfeim/cli-bearpublish) | Swift | Static site generator from Bear notes |
| [joisig.com](https://joisig.com/bearly-a-cms) | Elixir/Phoenix | Full website powered by Bear — tagged notes become pages |
| bearblogr | — | Bear as CMS for static blogs |

### Migration

| Project | Tech | What it does |
|---|---|---|
| [Obsidian Importer](https://help.obsidian.md/import/bear) | — | Official Obsidian plugin, handles Bear tags/attachments |
| [jonathanmcmahon/keep2bear](https://github.com/jonathanmcmahon/keep2bear) | Python | Google Keep → Bear |
| [crock/markdown-to-bear](https://github.com/crock/markdown-to-bear) | JavaScript | Markdown files ↔ Bear format |

### Editor Integrations

| Project | Tech | What it does |
|---|---|---|
| [vxe/bear.el](https://github.com/vxe/bear.el) | Emacs Lisp | x-callback-url wrapper for Emacs |
| [Raycast extension](https://www.raycast.com/hmarr/bear) | TypeScript | Search/open/create notes from Raycast (SQLite read + xcallback write) |
| Alfred Workflow (in [Bear Power Pack](https://github.com/sbusso/Bear-Power-Pack)) | — | Create and search via Alfred |

### Sync & Other

| Project | Tech | What it does |
|---|---|---|
| [d4rkd3v1l/BearSync](https://github.com/d4rkd3v1l/BearSync) | Swift | Sync Bear notes between accounts via git |
| [calebporzio/bear-sync](https://github.com/calebporzio/bear-sync) | PHP/Laravel | Eloquent models for Bear SQLite (archived) |
| [beyond2060/bear-helper](https://github.com/beyond2060/bear-helper) | Python | macOS menubar app — journal entries, project notes |
| [Bear Power Pack](https://github.com/sbusso/Bear-Power-Pack) | Mixed | Curated collection: iOS workflows, macOS shortcuts, importers, exporters |

### Creative / Unusual Uses
- **Bear as full CMS**: joisig.com runs entirely from tagged Bear notes (layouts/templates are also notes)
- **Daily journaling**: Shortcuts pulling weather + calendar + tasks into timestamped notes
- **"On This Day"**: Shortcuts finding journal entries from same date in prior years
- **Security research**: [Wojciech Regula](https://wojciechregula.blog/post/stealing-bear-notes-with-url-schemes/) found Bear's API tokens were derived from MD5 of predictable dates (fixed 2019)
- **Bear as Jekyll/Hugo CMS**: pybear includes `bear_to_jekyll`

---

## Ideas Worth Implementing

### 1. Semantic Search (learn: embeddings, vector similarity)
Embed all 6,234 notes using sentence-transformers (all-MiniLM-L6-v2), store vectors, find notes by meaning not just keywords. "Find notes about deployment strategies" returns relevant notes even if they don't contain those exact words.

### 2. Knowledge Graph Visualization (learn: graph algorithms, networkx, visualization)
Build graph from ZSFNOTEBACKLINK (note-to-note links) + Z_5TAGS (note-to-tag). Detect clusters, find orphaned notes, visualize with Streamlit or D3.

### 3. RAG Pipeline Over Personal Notes (learn: RAG, chunking, retrieval, LLM prompting)
Full pipeline: chunk notes → embed → store in vector DB (ChromaDB/FAISS) → query with natural language → LLM generates answer citing your notes.

### 4. Smart Export (learn: markdown parsing, file I/O, tree structures)
Export notes to folder hierarchy matching tag structure. Handle images, attachments, inter-note links. Configurable formats (markdown, HTML, PDF).

### 5. Bulk Operations (learn: x-callback-url, transaction safety)
Find/replace across all notes, bulk re-tag, merge duplicate notes, clean up orphaned tags.

### 6. Note Analytics Dashboard (learn: pandas, data viz, Streamlit)
Writing frequency over time, tag usage heatmap, orphaned notes, largest notes, stale notes, todo completion rates.

### 7. Daily Digest / Summary (learn: LLM summarization)
Auto-summarize recently modified notes, surface connections between today's edits and older notes.

### 8. MCP Server (learn: Model Context Protocol, tool design)
Build your own MCP server from scratch — expose Bear read/write as tools for Claude. Better than using an existing one if the goal is to learn.

### 9. Advanced Search (learn: SQL full-text search, ranking)
Search by content + title, sort by created/modified time, relevance ranking. Explore SQLite FTS5 for full-text indexing.
**PARTIALLY DONE**: title + text search with sort/order enums implemented. Remaining: attachment OCR text search (ZSFNOTEFILE.ZSEARCHTEXT), relevance ranking, FTS5.

### 17. Attachment OCR Search (learn: SQL joins, multi-table search)
Bear stores OCR-extracted text from PDFs and images in ZSFNOTEFILE.ZSEARCHTEXT. Join with ZSFNOTE to find notes where attachment content matches search terms.

### 10. Duplicate Detection & Cleanup (learn: text similarity, x-callback-url writes)
Find notes with similar titles or content. Delete duplicates via x-callback-url. Could use fuzzy matching or embeddings for near-duplicates.

### 11. Tag Cleanup & Organization (learn: string manipulation, tree structures)
Find unused tags, merge similar tags (e.g. "k8s" and "kubernetes"), visualize tag hierarchy as a tree, suggest re-tagging.

### 12. Note Grouping & Merging (learn: text similarity, clustering)
Find notes on the same subject, merge them into consolidated notes.

### 13. Template-Based Note Creation (learn: string templating, x-callback-url)
Create daily journal notes, meeting notes from templates. Date stamps, recurring sections, pre-filled tags.

### 14. Note Health Report (learn: data analysis, SQL)
Orphaned notes (no tags), empty notes, broken wiki-links, stale todos, notes not modified in years.

### 15. CLI Tool (learn: click/typer, packaging)
`bear search "python"`, `bear tags`, `bear stats` from terminal — proper CLI with subcommands.

### 16. Writing Stats (learn: pandas, data viz)
Notes per week/month over time, average note length, most active periods, tag usage trends.

### 18. Bear Health Check (learn: integration testing, polling)
Detect if Bear is running and ready to accept commands. Approach: create a temp note via x-callback-url, poll SQLite to see if it appeared, trash it. Confirms Bear is running, unlocked, and processing commands.

### 19. Bear Precondition Check (learn: subprocess, process detection)
Simple `pgrep -x "Bear"` check before write operations. Raise error with helpful message if Bear isn't running. Note: cannot detect if Bear is locked (fingerprint pending).

### 20. Meeting Note from Outlook Calendar (learn: Outlook API/AppleScript, calendar integration)
Pull meeting details (title, attendees, time, agenda) from Outlook/macOS Calendar and create a pre-filled Bear note. Could use AppleScript, `icalBuddy` CLI, or Microsoft Graph API.

### 21. Note from Jira Ticket (learn: REST API, Jira integration)
Fetch Jira ticket details (summary, description, assignee, status, comments) and create a Bear note. Could use Jira REST API or `jira` Python library. Useful for tracking work context alongside notes.

### 22. Daily Journal from Template (learn: string templates, date formatting)
`bear journal` creates today's journal note with date header, recurring sections, pre-filled `.journal/YYYY/MM/DD` tag. Match existing journal format.

### 23. Meeting Note from Template (learn: string templates)
`bear meeting "standup"` creates a meeting note with title, date, attendees section, agenda, action items template.

### 24. Advanced Search — Multi-term AND (learn: dynamic SQL, string splitting)
`bear search "latitude longitude"` — split by spaces, require ALL terms. Immediate improvement over single-term LIKE.

### 25. Advanced Search — Title-first Ranking (learn: SQL CASE, result sorting)
Show title matches before body-only matches. Uses SQL `CASE WHEN ZTITLE LIKE :term THEN 1 ELSE 2 END` for ordering.

### 26. Advanced Search — FTS5 Full-Text Index (learn: SQLite FTS5, relevance ranking)
Create a virtual FTS5 table mirroring ZSFNOTE. Enables tokenized search with BM25 ranking. Challenge: FTS table needs to be rebuilt when Bear updates notes.

### 27. Advanced Search — Boolean Expressions (learn: parsing, query building)
`"latitude AND longitude NOT gps"` — parse logic expressions into SQL. Could use a simple recursive descent parser.

### 28. Advanced Search — Fuzzy Matching (learn: string distance algorithms)
Find "longitude" even if user types "longtude". Levenshtein distance or trigram matching.

### 29. Advanced Search — Semantic/Vector Search (learn: embeddings, FAISS/ChromaDB)
Embed all notes, search by meaning. "Distance between coordinates" finds the latitude note. Most powerful but requires ML dependencies.

### 30. Clickable Note Links in CLI Output (learn: terminal hyperlinks, Rich markup)
In table output, render note titles as clickable links using `bear://open-note?id=<identifier>`. Modern terminals (iTerm2, macOS Terminal, VS Code) support OSC 8 hyperlinks. Rich supports this with `[link=URL]text[/link]` markup. Cmd+click opens the note directly in Bear.

### 31. Import Markdown Files (learn: file I/O, pathlib, text parsing)
`bear import notes/meeting.md` or `bear import notes/ --recursive` to bulk-import markdown files into Bear. Extract title from first `# heading` or filename. Optionally derive tags from folder structure (`notes/work/meeting.md` → tag `work`). Handle images/attachments via Bear's x-callback-url `file` param. Consider bulk performance (1s sleep per note).

---

## Technology Decision

**Chosen: Python**

Reasons:
- `sqlite3` is in the standard library (zero config)
- 50-100ms startup vs 2-6s for Spring Boot
- 20-40MB memory vs 150-400MB for JVM
- AI/ML ecosystem is Python-first (sentence-transformers, faiss, chromadb, anthropic SDK)
- Official MCP SDK is Python-first
- Every Bear automation project in the wild uses Python, TypeScript, or Swift — none use Java
- Instant iteration: change a line, run immediately

Spring Boot would work technically but is designed for enterprise server apps — overkill for local desktop tooling.
