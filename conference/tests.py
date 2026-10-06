from django.test import TestCase


class IndexTests(TestCase):
    def test_home_renders(self):
        response = self.client.get("/", secure=True)
        self.assertContains(response, "M2ISDA")
        self.assertContains(response, "lamo@univ.edu.dj")

    def test_static_references_resolved(self):
        response = self.client.get("/", secure=True)
        self.assertNotContains(response, "{% static")
        self.assertNotContains(response, "{% verbatim")

    def test_healthz(self):
        response = self.client.get("/healthz", secure=True)
        self.assertEqual(response.content, b"ok")
