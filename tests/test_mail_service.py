import base64
import importlib.util
import pathlib
import sys
import unittest


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "mail_service.py"
SPEC = importlib.util.spec_from_file_location("mail_service", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


class MailServiceTests(unittest.TestCase):
    def test_build_aktuelles_post_creates_fixed_article_structure(self):
        html = module.build_aktuelles_post(
            title="Sommernachmittag am Platz",
            text="Die Mannschaft und die Familie haben den Nachmittag gemeinsam auf dem Trainingsgelände verbracht.",
            image_src="images/aktuelles_01_rudow_fv.png",
            alt_text="Sommernachmittag am Platz",
            tag="To be posted",
            date="2026-10-04",
        )

        self.assertIn('<article class="upload-card">', html)
        self.assertIn('<div class="upload-media">', html)
        self.assertIn('src="images/aktuelles_01_rudow_fv.png"', html)
        self.assertIn('<h3>Sommernachmittag am Platz</h3>', html)
        self.assertIn('2026-10-04', html)
        self.assertIn('Die Mannschaft und die Familie', html)

    def test_sanitize_text_removes_script_tags(self):
        cleaned = module.sanitize_text("<script>alert('x')</script><p>Hallo Welt</p>")
        self.assertNotIn('<script', cleaned.lower())
        self.assertIn('Hallo Welt', cleaned)

    def test_is_allowed_sender_checks_allowlist_case_insensitive(self):
        self.assertTrue(module.is_allowed_sender("Editor@Example.org", {"editor@example.org"}))
        self.assertFalse(module.is_allowed_sender("someone@example.org", {"editor@example.org"}))

    def test_extract_message_parts_validates_sender_and_image_for_post_messages(self):
        image_data = base64.b64encode(b"fake-image-bytes")
        raw_message = (
            "From: Editor@Example.org\r\n"
            "To: aktuelles@example.org\r\n"
            "Subject: post Test Title\r\n"
            "MIME-Version: 1.0\r\n"
            "Content-Type: multipart/mixed; boundary=\"boundary123\"\r\n\r\n"
            "--boundary123\r\n"
            "Content-Type: text/plain; charset=utf-8\r\n\r\n"
            "Hallo Welt\r\n"
            "--boundary123\r\n"
            "Content-Type: image/png; name=\"post.png\"\r\n"
            "Content-Disposition: attachment; filename=\"post.png\"\r\n"
            "Content-Transfer-Encoding: base64\r\n\r\n"
            f"{image_data.decode()}\r\n"
            "--boundary123--\r\n"
        )

        payload = module.extract_message_parts(raw_message, {"editor@example.org"})
        self.assertEqual(payload["sender"], "Editor@Example.org")
        self.assertEqual(payload["title"], "Test Title")
        self.assertIn("Hallo Welt", payload["text"])
        self.assertEqual(payload["image_name"], "post.png")
        self.assertIn(b"fake-image-bytes", payload["image_bytes"])

    def test_extract_message_parts_allows_delete_messages_without_text_or_image(self):
        raw_message = (
            "From: Editor@Example.org\r\n"
            "To: aktuelles@example.org\r\n"
            "Subject: del Neuer Titel\r\n"
            "MIME-Version: 1.0\r\n"
            "Content-Type: text/plain; charset=utf-8\r\n\r\n"
            "ignored body\r\n"
        )

        payload = module.extract_message_parts(raw_message, {"editor@example.org"})
        self.assertTrue(payload["is_delete_command"])
        self.assertEqual(payload["delete_title"], "Neuer Titel")
        self.assertEqual(payload["text"], "")
        self.assertEqual(payload["image_bytes"], b"")

    def test_load_allowlist_reads_comments_and_whitespace(self):
        allowlist = module.load_allowlist_from_text("   # comment\nEditor@example.org\n  another@example.org  \n")
        self.assertEqual(allowlist, {"editor@example.org", "another@example.org"})

    def test_parse_post_command_matches_post_title_pattern(self):
        self.assertEqual(module.parse_post_command("post Sommernachmittag am Platz"), "Sommernachmittag am Platz")
        self.assertEqual(module.parse_post_command("POST   Sommernachmittag am Platz  "), "Sommernachmittag am Platz")
        self.assertIsNone(module.parse_post_command("Sommernachmittag am Platz"))

    def test_parse_post_command_strips_surrounding_whitespace_and_normalizes_spaces(self):
        self.assertEqual(module.parse_post_command("  post   Neuer   SUPER   Test   "), "Neuer SUPER Test")
        self.assertEqual(module.parse_delete_command("  del   Neuer   SUPER   Test   "), "Neuer SUPER Test")

    def test_normalize_title_strips_whitespace_and_collapses_spaces(self):
        self.assertEqual(module.normalize_title("  Neuer   SUPER   Test  \n"), "Neuer SUPER Test")

    def test_parse_delete_command_matches_del_title_pattern(self):
        self.assertEqual(module.parse_delete_command("del Sommernachmittag am Platz"), "Sommernachmittag am Platz")
        self.assertEqual(module.parse_delete_command("DEL   Sommernachmittag am Platz  "), "Sommernachmittag am Platz")
        self.assertIsNone(module.parse_delete_command("Sommernachmittag am Platz"))

    def test_extract_message_parts_requires_post_or_del_about(self):
        image_data = base64.b64encode(b"fake-image-bytes")
        raw_message = (
            "From: Editor@Example.org\r\n"
            "To: aktuelles@example.org\r\n"
            "Subject: Hello world\r\n"
            "MIME-Version: 1.0\r\n"
            "Content-Type: multipart/mixed; boundary=\"boundary123\"\r\n\r\n"
            "--boundary123\r\n"
            "Content-Type: text/plain; charset=utf-8\r\n\r\n"
            "Hallo Welt\r\n"
            "--boundary123\r\n"
            "Content-Type: image/png; name=\"post.png\"\r\n"
            "Content-Disposition: attachment; filename=\"post.png\"\r\n"
            "Content-Transfer-Encoding: base64\r\n\r\n"
            f"{image_data.decode()}\r\n"
            "--boundary123--\r\n"
        )

        with self.assertRaises(ValueError):
            module.extract_message_parts(raw_message, {"editor@example.org"})

    def test_delete_aktuelles_posts_by_title_removes_matching_cards(self):
        html_document = """
        <div class=\"upload-parent-box\">
            <article class=\"upload-card\">
                <div class=\"upload-copy\"><h3>Sommernachmittag am Platz</h3><p>old text</p></div>
            </article>
            <article class=\"upload-card\">
                <div class=\"upload-copy\"><h3>Training mit Teamgeist</h3><p>keep me</p></div>
            </article>
        </div>
        """

        updated = module.delete_aktuelles_posts_by_title(html_document, "Sommernachmittag am Platz")

        self.assertNotIn("Sommernachmittag am Platz", updated)
        self.assertIn("Training mit Teamgeist", updated)
        self.assertIn("upload-parent-box", updated)

    def test_delete_aktuelles_posts_by_title_ignores_surrounding_whitespace(self):
        html_document = """
        <div class=\"upload-parent-box\">
            <article class=\"upload-card\">
                <div class=\"upload-copy\"><h3>  Neuer SUPER Test  </h3><p>old text</p></div>
            </article>
            <article class=\"upload-card\">
                <div class=\"upload-copy\"><h3>Anderer Beitrag</h3><p>keep me</p></div>
            </article>
        </div>
        """

        updated = module.delete_aktuelles_posts_by_title(html_document, "  Neuer   SUPER   Test  ")

        self.assertNotIn("Neuer SUPER Test", updated)
        self.assertIn("Anderer Beitrag", updated)

    def test_delete_aktuelles_posts_by_title_removes_only_matching_article(self):
        html_document = """
        <div class=\"upload-parent-box\">
            <article class=\"upload-card\">
                <div class=\"upload-copy\"><h3>Letzter Spieltag</h3><p>keep me</p></div>
            </article>
            <article class=\"upload-card\">
                <div class=\"upload-copy\"><h3>Gemeinsam vor dem Anpfiff</h3><p>delete me</p></div>
            </article>
            <article class=\"upload-card\">
                <div class=\"upload-copy\"><h3>Nachster Spieltag</h3><p>keep me too</p></div>
            </article>
        </div>
        """

        updated = module.delete_aktuelles_posts_by_title(html_document, "Gemeinsam vor dem Anpfiff")

        self.assertIn("Letzter Spieltag", updated)
        self.assertNotIn("Gemeinsam vor dem Anpfiff", updated)
        self.assertIn("Nachster Spieltag", updated)


if __name__ == "__main__":
    unittest.main()
