import html
import json
import re
from pathlib import Path

from django.test import TestCase, override_settings


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

    @override_settings(ALLOWED_HOSTS=["m2isda-2027.onrender.com", "m2isda.com", "localhost"])
    def test_legacy_onrender_host_redirects_to_canonical_domain(self):
        response = self.client.get("/?x=1", secure=True, HTTP_HOST="m2isda-2027.onrender.com")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "https://m2isda.com/?x=1")

    @override_settings(ALLOWED_HOSTS=["m2isda-2027.onrender.com", "m2isda.com", "localhost"])
    def test_healthz_is_not_redirected_on_legacy_host(self):
        response = self.client.get("/healthz", secure=True, HTTP_HOST="m2isda-2027.onrender.com")
        self.assertEqual(response.status_code, 200)

    @override_settings(ALLOWED_HOSTS=["m2isda.com", "localhost"])
    def test_canonical_domain_is_served_not_redirected(self):
        self.assertEqual(self.client.get("/", secure=True, HTTP_HOST="m2isda.com").status_code, 200)

    def test_robots_and_sitemap(self):
        self.assertContains(self.get("/robots.txt"), "Sitemap: https://m2isda.com/sitemap.xml")
        self.assertContains(self.get("/sitemap.xml"), "<loc>https://m2isda.com/</loc>")

    def test_special_issue_block(self):
        page = html.unescape(self.get("/").content.decode())
        for needle in (
            "Mathematical and Computational Applications (MCA) — MDPI",
            "https://www.mdpi.com/journal/mca/special_issues/UYV2YYZR4Q",
            "http://mdpi.com/si/293143",
            "Mathematical Modeling, Optimization and Innovations in Advanced Data Science (M2ISDA 2027)",
            "Dr. Yahyeh Souleiman", "Dr. Nathalie Verdiere", "Dr. Hacene Djellout",
            "Dr. Legesse Lemecha Obsu", "Prof. Dr. Raluca Eftimie",
            "30 septembre 2027", "30 September 2027", "CiteScore 2.8",
        ):
            self.assertIn(needle, page)

    def test_old_publication_placeholder_cards_removed(self):
        page = html.unescape(self.get("/").content.decode())
        self.assertNotIn("Revue d’accueil", page)
        self.assertNotIn("seront annoncés sur cette page", page)
        self.assertIn("Mathematical and Computational Applications (MCA)", page)

    def test_organising_committee_has_six_permanent_members(self):
        page = html.unescape(self.get("/").content.decode())
        for name in ("Dr Yahyeh Souleiman", "Dr Liban Ismail", "Dr Souleiman Omar", "Dr Doualeh Ali",
                     "Dr Houssein Ahmed Assoweh", "Dr Souleiman Isman Guedi"):
            self.assertIn(name, page)
        self.assertIn("Six enseignants-chercheurs permanents", page)
        self.assertIn("assoweh", page)
        self.assertIn("guedi", page)
