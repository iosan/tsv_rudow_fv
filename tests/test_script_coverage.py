import importlib.util
import pathlib
import sys
from datetime import datetime, timedelta
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def load_module(name: str, relative_path: str):
    module_path = pathlib.Path(__file__).resolve().parents[1] / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


process_mod = load_module("process_aktuelles_mail_vps", "scripts/process_aktuelles_mail_vps.py")
publish_mod = load_module("publish_aktuelles_mail_vps", "scripts/publish_aktuelles_mail_vps.py")
cleanup_mod = load_module("cleanup_aktuelles_mail_queue", "scripts/cleanup_aktuelles_mail_queue.py")
fetch_mod = load_module("fetch_league_data", "scripts/fetch_league_data.py")


def test_process_module_normalizes_titles_and_parses_commands():
    assert process_mod.normalize_title("  Mock   Test   Title  ") == "Mock Test Title"
    assert process_mod.parse_post_command("post Mock Test Title") == "Mock Test Title"
    assert process_mod.parse_delete_command("del Mock Test Title") == "Mock Test Title"
    assert process_mod.parse_title_command("post   Mock   Test   Title") == ("post", "Mock Test Title")


def test_process_module_extract_text_deduplicates_repeated_multipart_body_parts():
    msg = MIMEMultipart()
    msg["From"] = "editor@example.org"
    msg["Subject"] = "post Mock Test Title"
    msg.attach(MIMEText("This is the body text for the post.", "plain", "utf-8"))
    msg.attach(MIMEText("This is the body text for the post.", "html", "utf-8"))

    text = process_mod.extract_text(msg)
    assert text.count("This is the body text for the post.") == 1


def test_process_module_extract_text_deduplicates_repeated_paragraphs_within_one_body():
    msg = MIMEMultipart()
    msg["From"] = "editor@example.org"
    msg["Subject"] = "post Mock Test Title"
    repeated_paragraph = (
        "Vor dem Heimspiel stand die Halle voller Erwartung. Fans, Eltern, Spieler und Helfer "
        "trafen sich ein paar Minuten vor dem Start und tauschten sich über die Woche und die "
        "Ziele der kommenden Begegnung aus. Solche Momente zeigen, wie wichtig die Rolle des "
        "Fördervereins für den Vereinsalltag und die sportliche Stimmung ist."
    )
    msg.attach(MIMEText(f"{repeated_paragraph} {repeated_paragraph}", "plain", "utf-8"))

    text = process_mod.extract_text(msg)
    assert text.count(repeated_paragraph) == 1


def test_process_module_strips_html_markup_from_mail_body_text():
    msg = MIMEMultipart()
    msg["From"] = "editor@example.org"
    msg["Subject"] = "post Mock Test Title"
    msg.attach(MIMEText('<p>Visible text</p><script>alert(1)</script><style>body{color:red}</style>', "html", "utf-8"))

    text = process_mod.extract_text(msg)
    assert "Visible text" in text
    assert "<p>" not in text
    assert "alert" not in text.lower()
    assert "body{color:red}" not in text.lower()


def test_publish_module_builds_article_and_deletes_matching_posts(tmp_path, monkeypatch):
    html_path = tmp_path / "aktuelles.html"
    html_path.write_text(
        '<div class="upload-parent-box">\n<article class="upload-card"><div class="upload-copy"><h3>Keep Me</h3></div></article>\n</div>',
        encoding="utf-8",
    )
    monkeypatch.setattr(publish_mod, "SITE_HTML", html_path)
    monkeypatch.setattr(publish_mod, "SITE_IMAGES", tmp_path / "images")

    article = publish_mod.build_article(
        title="Mock Test Title",
        text="A short article body.",
        image_src="images/mock-image.png",
        alt_text="Mock Test Title",
        date_str="2026-10-04",
    )
    assert "<article class=\"upload-card\">" in article
    assert "Mock Test Title" in article
    assert "images/mock-image.png" in article

    after_delete = publish_mod.delete_matching_posts(
        '<div class="upload-parent-box"><article class="upload-card"><div class="upload-copy"><h3>Mock Test Title</h3></div></article></div>',
        "Mock Test Title",
    )
    assert "Mock Test Title" not in after_delete


def test_publish_module_processes_raw_post_email(tmp_path, monkeypatch):
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "allowlist.txt").write_text("editor@example.org\n", encoding="utf-8")
    html_path = tmp_path / "aktuelles.html"
    html_path.write_text('<div class="upload-parent-box">\n</div>', encoding="utf-8")
    image_dir = tmp_path / "images"

    monkeypatch.setattr(publish_mod, "BASE_DIR", tmp_path)
    monkeypatch.setattr(publish_mod, "STORAGE_DIR", storage_dir)
    monkeypatch.setattr(publish_mod, "SITE_HTML", html_path)
    monkeypatch.setattr(publish_mod, "SITE_IMAGES", image_dir)

    msg = MIMEMultipart()
    msg["From"] = "editor@example.org"
    msg["To"] = "aktuelles@example.org"
    msg["Subject"] = "post Mock Test Title"
    msg.attach(MIMEText("This is the body text for the post.", "plain", "utf-8"))
    image = MIMEImage(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc``\x00\x00\x00\x02\x00\x01\xe5\x27\xd8\xcf\x00\x00\x00\x00IEND\xaeB`\x82", _subtype="png")
    image.add_header("Content-Disposition", "attachment", filename="mock-image.png")
    msg.attach(image)

    raw_file = storage_dir / "raw-test.eml"
    raw_file.write_bytes(msg.as_bytes())

    processed = publish_mod.process_raw_message(raw_file)
    assert "Mock Test Title" in processed
    assert html_path.read_text(encoding="utf-8").count("<article class=\"upload-card\">") >= 1
    assert not raw_file.exists()


def test_cleanup_module_removes_stale_raw_messages(tmp_path, monkeypatch):
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()
    html_path = tmp_path / "aktuelles.html"
    html_path.write_text(
        '<div class="upload-parent-box">\n<article class="upload-card"><div class="upload-copy"><h3>Mock Test Title</h3></div></article>\n</div>',
        encoding="utf-8",
    )

    monkeypatch.setattr(cleanup_mod, "STORAGE_DIR", storage_dir)
    monkeypatch.setattr(cleanup_mod, "SITE_HTML", html_path)

    raw_file = storage_dir / "raw-stale.eml"
    raw_file.write_bytes(b"From: editor@example.org\nSubject: del Mock Test Title\n\n")

    cleaned = cleanup_mod.clean_queue()
    assert cleaned == 1
    assert not raw_file.exists()
    assert "Mock Test Title" not in html_path.read_text(encoding="utf-8")


def test_publish_module_only_deletes_matching_article_title():
    html = (
        '<div class="upload-parent-box">'
        '<article class="upload-card"><div class="upload-copy"><h3>Letzter Spieltag</h3></div></article>'
        '<article class="upload-card"><div class="upload-copy"><h3>Gemeinsam vor dem Anpfiff</h3></div></article>'
        '<article class="upload-card"><div class="upload-copy"><h3>Nachster Spieltag</h3></div></article>'
        '</div>'
    )

    updated = publish_mod.delete_matching_posts(html, "Gemeinsam vor dem Anpfiff")
    assert "Letzter Spieltag" in updated
    assert "Gemeinsam vor dem Anpfiff" not in updated
    assert "Nachster Spieltag" in updated


def test_publish_module_keeps_outer_page_article_wrapper_intact():
    html = (
        '<main><article><h2>Aktuelles</h2>'
        '<div class="upload-parent-box">'
        '<article class="upload-card"><div class="upload-copy"><h3>Title A</h3></div></article>'
        '<article class="upload-card"><div class="upload-copy"><h3>Title B</h3></div></article>'
        '</div></article></main>'
    )

    updated = publish_mod.delete_matching_posts(html, "Title A")
    assert "<article><h2>Aktuelles</h2>" in updated
    assert "Title B" in updated
    assert "Title A" not in updated


def test_fetch_league_data_helpers_work_as_expected():
    assert fetch_mod.normalize_space("  alpha   beta  ") == "alpha beta"
    assert fetch_mod.strip_tags("<p>Hello <strong>world</strong></p>") == "Hello world"
    assert fetch_mod.first_int("Rank 12") == 12
    assert fetch_mod.dedupe_matches([
        {"matchUrl": "a", "dateLabel": "1", "homeTeam": "A", "awayTeam": "B"},
        {"matchUrl": "a", "dateLabel": "1", "homeTeam": "A", "awayTeam": "B"},
        {"matchUrl": "b", "dateLabel": "2", "homeTeam": "A", "awayTeam": "B"},
    ]) == [
        {"matchUrl": "a", "dateLabel": "1", "homeTeam": "A", "awayTeam": "B"},
        {"matchUrl": "b", "dateLabel": "2", "homeTeam": "A", "awayTeam": "B"},
    ]


def test_fetch_league_data_parse_and_match_helpers():
    assert fetch_mod.normalize_date_label("12.04.2025 18:30", 2025) == "12.04.2025 18:30"
    assert fetch_mod.parse_datetime_iso("12.04.2025 18:30", 2025) == "2025-04-12T18:30:00"
    assert fetch_mod.extract_match_id("https://example.com/spiel/ABC123") == "ABC123"
    assert fetch_mod.normalize_score_text("2 : 1") == "2 : 1"
    assert fetch_mod.parse_result_state({"events": [{"description": "Abpfiff", "type_id": 29}]}) == "official"

    rows = fetch_mod.parse_table_rows(
        '<tr><td>1</td><td><a class="club-wrapper">TSV Rudow</a></td><td>10</td><td>7</td><td>2</td><td>1</td><td>20:10</td><td>10</td><td>23</td></tr>'
    )
    assert rows[0]["team"] == "TSV Rudow"
    assert rows[0]["points"] == 23

    now = datetime.now()
    past = (now - timedelta(days=2)).isoformat()
    future = (now + timedelta(days=2)).isoformat()
    last_result, next_match = fetch_mod.choose_last_and_next([
        {"dateTime": past, "status": "played", "rowIndex": 1},
        {"dateTime": future, "status": "upcoming", "rowIndex": 2},
    ])
    assert last_result["status"] == "played"
    assert next_match["status"] == "upcoming"


def test_fetch_league_data_build_homepage_projection(monkeypatch):
    club_page = """
    <h4><a href="/mannschaft/club/1/team-id/42">Herren - TSV Rudow</a></h4>
    <a href="/spieltagsuebersicht/staffel/ABC123">Staffel</a>
    """

    monkeypatch.setattr(fetch_mod, "resolve_team_source", lambda html, cfg: {"teamUrl": "https://example.com/team", "teamId": "42", "staffelId": "ABC123"})
    monkeypatch.setattr(fetch_mod, "fetch_text", lambda url: {
        "https://example.com/ajax.actual.table/-/staffel/ABC123": "<tr><td>1</td><td><a class='club-wrapper'>TSV Rudow</a></td><td>10</td><td>7</td><td>2</td><td>1</td><td>20:10</td><td>10</td><td>23</td></tr>",
        "https://example.com/spielplan/-/staffel/ABC123": "<tr class='row-competition'><td>10.04.2025</td></tr><tr><td><a class='club-wrapper'>TSV Rudow</a></td><td><a class='club-wrapper'>Musterverein</a></td><td><a href='/spiel/XYZ987'>2 : 1</a></td></tr>",
    }.get(url, ""))

    payload = fetch_mod.build_homepage_projection([
        {
            "name": "TSV Rudow",
            "standing": {"rank": 1, "played": 10, "points": 23, "goalDiff": 10},
            "lastResult": {"homeTeam": "TSV Rudow", "awayTeam": "Musterverein", "opponent": "Musterverein", "location": "Heim", "dateLabel": "10.04.2025", "score": "2 : 1", "scoreAvailable": True, "resultState": "official", "matchUrl": "https://example.com/spiel/XYZ987"},
            "nextMatch": {"homeTeam": "TSV Rudow", "awayTeam": "Demo FC", "opponent": "Demo FC", "location": "Heim", "dateLabel": "18.04.2025", "matchUrl": "https://example.com/spiel/NEXT123"},
        }
    ])

    assert payload["tableRows"][0]["team"] == "TSV Rudow"
    assert payload["recentResults"][0]["score"] == "2 : 1"
    assert payload["upcomingMatches"][0]["opponent"] == "Demo FC"
