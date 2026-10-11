from django.test import TestCase


class SiteTests(TestCase):
    def get(self, path):
        return self.client.get(path, secure=True)

    def test_home_renders(self):
        response = self.get("/")
        self.assertContains(response, "M2ISDA")
        self.assertContains(response, "lamo@univ.edu.dj")
        self.assertContains(response, "Dix conférenciers")

    def test_no_unrendered_template_tags(self):
        response = self.get("/")
        self.assertNotContains(response, "{% ")
        self.assertNotContains(response, "{{ ")

    def test_all_speakers_and_partners_present(self):
        html = self.get("/").content.decode()
        for name in ("Ramsès Djidjou-Demasse", "Daud Ali Aser", "INSTAD", "Mogadishu University"):
            self.assertIn(name, html)

    def test_english_translations_embedded(self):
        self.assertContains(self.get("/"), 'data-en="Ten speakers,"')

    def test_healthz(self):
        self.assertEqual(self.get("/healthz").content, b"ok")

    def test_tex_download(self):
        response = self.get("/modele-resume.tex")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn(b"\documentclass", response.content)
