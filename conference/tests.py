import html
import json
import re
from pathlib import Path

from django.test import TestCase


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


class SiteTests(TestCase):
    def get(self, path):
        return self.client.get(path, secure=True)

    def test_home_renders(self):
        response = self.get("/")
        self.assertContains(response, "M2ISDA")
        self.assertContains(response, "lamo@univ.edu.dj")

    def test_original_content_is_preserved(self):
        """Tous les textes de la version initiale (FR et EN) doivent rester présents."""
        pairs = json.loads((Path(__file__).parent / "tests_data" / "original_content.json").read_text(encoding="utf-8"))
        page = norm(html.unescape(self.get("/").content.decode()))
        missing = [(fr, en) for fr, en in pairs if norm(fr) not in page or norm(en) not in page]
        self.assertEqual(missing, [])

    def test_top_menu_has_the_ten_original_entries_in_order(self):
        page = self.get("/").content.decode()
        start = page.index('id="topnav"')
        side = page[start:page.index("</nav>", start)]
        hrefs = re.findall(r'href="#(\w+)"', side)
        self.assertEqual(hrefs, ["accueil", "organisation", "scientifique", "conferenciers", "dates",
                                 "inscription", "programme", "publications", "soumission", "partenaires"])
        for page_id in hrefs:
            self.assertIn(f'id="{page_id}" class="page"', page)

    def test_lamo_and_university_logos_present(self):
        page = self.get("/").content.decode()
        self.assertIn("lamo-logo", page)
        self.assertIn("ud-logo", page)

    def test_no_unrendered_template_tags(self):
        response = self.get("/")
        self.assertNotContains(response, "{% ")
        self.assertNotContains(response, "{{ ")

    def test_all_speakers_and_partners_present(self):
        html_page = self.get("/").content.decode()
        for name in ("Ramsès Djidjou-Demasse", "Daud Ali Aser", "INSTAD", "Mogadishu University"):
            self.assertIn(name, html_page)

    def test_healthz(self):
        self.assertEqual(self.get("/healthz").content, b"ok")

    def test_tex_download_is_the_original_template(self):
        response = self.get("/modele-resume.tex")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn(b"Modele de resume", response.content)

    def test_canonical_domain_declared(self):
        page = self.get("/").content.decode()
        self.assertIn('<link rel="canonical" href="https://m2isda.com/">', page)
        self.assertIn('content="https://m2isda.com/static/', page)
