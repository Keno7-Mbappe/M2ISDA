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

    def test_top_menu_keeps_the_ten_original_entries_in_order_and_adds_two(self):
        page = self.get("/").content.decode()
        start = page.index('id="topnav"')
        side = page[start:page.index("</nav>", start)]
        hrefs = re.findall(r'href="#(\w+)"', side)
        self.assertEqual([h for h in hrefs if h not in ("thematiques", "participants")],
                         ["accueil", "organisation", "scientifique", "conferenciers", "dates",
                          "inscription", "programme", "publications", "soumission", "partenaires"])
        self.assertEqual(hrefs, ["accueil", "organisation", "scientifique", "conferenciers", "thematiques", "dates",
                                 "inscription", "participants", "programme", "publications", "soumission", "partenaires"])
        for page_id in hrefs:
            self.assertIn(f'id="{page_id}" class="page"', page)

    def test_topics_page_shows_the_eight_axes_with_an_image_each(self):
        page = html.unescape(self.get("/").content.decode())
        section = page[page.index('id="thematiques" class="page"'):page.index('id="dates" class="page"')]
        self.assertEqual(section.count('class="theme rv"'), 8)
        self.assertEqual(section.count("conference/img/themes/"), 8)
        self.assertIn("Modélisation épidémiologique et santé publique", section)

    def test_participants_page_is_an_alphabetical_list_without_photos(self):
        from .participants import sort_key
        page = html.unescape(self.get("/").content.decode())
        section = page[page.index('id="participants" class="page"'):page.index('id="programme" class="page"')]
        names = re.findall(r'<b class="prow-name">(.*?)</b>', section)
        self.assertEqual(len(names), 27)
        self.assertEqual(names, sorted(names, key=sort_key))
        self.assertEqual(names[:3], ["Abdisalam Hassan", "Abdoulrahman Farah", "Ali Mohamed"])
        self.assertIn("Dr Doualeh Ali", names)
        self.assertNotIn("<img", section)
        self.assertIn('id="psearch"', section)
        self.assertIn("Université de Djibouti", section)

    def test_participants_page_has_a_world_map_with_one_pin_per_country(self):
        page = html.unescape(self.get("/").content.decode())
        section = page[page.index('id="participants" class="page"'):page.index('id="programme" class="page"')]
        self.assertIn('class="world-dots world-dots--on"', section)
        self.assertEqual(section.count('<button type="button" class="pin'), 6)
        self.assertEqual(section.count('class="pin pin--host"'), 1)
        for pays in ("France", "Maroc", "Sénégal", "Éthiopie", "Somalie", "Djibouti"):
            self.assertIn(f'data-q-fr="{pays}"', section)

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
        for name in ("Ramsès Djidjou-Demasse", "Daud Ali Aser", "Mogadishu University", "Le Havre Normandie"):
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

    def test_organising_committee_has_six_researchers(self):
        page = html.unescape(self.get("/").content.decode())
        org = page[page.index('id="organisation" class="page"'):page.index('id="scientifique" class="page"')]
        for name in ("Dr Yahyeh Souleiman", "Dr Liban Ismail", "Dr Souleiman Omar", "Dr Doualeh Ali", "Dr Souleiman Isman Guedi", "Dr Hassan Ali Barkad"):
            self.assertIn(name, org)
        self.assertNotIn("Assoweh", org)
        self.assertEqual(org[:org.index("Doctorants")].count("Maître de conférences"), 6)
        self.assertIn("Six enseignants-chercheurs, sept doctorants", org)
        self.assertNotIn("Membres permanents", page)

    def test_scientific_committee_includes_assoweh(self):
        page = html.unescape(self.get("/").content.decode())
        sci = page[page.index('id="scientifique" class="page"'):page.index('id="conferenciers" class="page"')]
        self.assertIn("Dr Houssein Ahmed Assoweh", sci)
        self.assertIn("assoweh", sci)
        self.assertIn("Dix enseignants-chercheurs de Djibouti", sci)
        block = sci[sci.index("Dr Houssein Ahmed Assoweh"):]
        self.assertIn("Maître de conférences, Université de Djibouti", block[:700])
        self.assertIn("Associate Professor, University of Djibouti", block[:700])
        self.assertIn("Djibouti</em>", block[:900].replace('<span data-en="Djibouti">', ''))
        self.assertEqual(sci.count('class="person rv"'), 10)

    def test_national_institutions_section_removed(self):
        page = html.unescape(self.get("/").content.decode())
        part = page[page.index('id="partenaires" class="page"'):]
        part = part[:part.index("</section>")]
        for gone in ("Institutions nationales", "National institutions", "INSTAD", "INSPD", "SGTD", "DPCS", "DPCR", "Hôpital militaire"):
            self.assertNotIn(gone, part)
        self.assertIn("Universités partenaires", part)
        self.assertEqual(part.count('class="partner partner--sm rv"'), 7)


class ParticipantsDataTests(TestCase):
    def test_initial_list_is_seeded(self):
        from .models import Participant
        self.assertEqual(Participant.objects.count(), 27)

    def test_new_participant_appears_on_the_page_and_the_map(self):
        from .models import Participant
        Participant.objects.create(name="Zoé Tremblay", institution="Université de Montréal", country="CA")
        page = html.unescape(self.client.get("/", secure=True).content.decode())
        self.assertIn("Zoé Tremblay", page)
        self.assertIn('data-q-fr="Canada"', page)
        self.assertEqual(page.count('class="prow"'), 28)

    def test_titles_do_not_disturb_alphabetical_order(self):
        from .participants import sort_key
        self.assertEqual(sort_key("Dr Yahyeh Souleiman"), "yahyeh souleiman")
        self.assertEqual(sort_key("Pr. Éric Lamy"), "eric lamy")
        self.assertLess(sort_key("Ali Mohamed"), sort_key("Dr Doualeh Ali"))
        self.assertLess(sort_key("Émile Zola"), sort_key("Zoé"))

    def test_country_lookup_accepts_french_english_and_codes(self):
        from .forms import country_code
        self.assertEqual(country_code("Maroc"), "MA")
        self.assertEqual(country_code("morocco"), "MA")
        self.assertEqual(country_code("sénégal"), "SN")
        self.assertEqual(country_code("fr"), "FR")
        self.assertEqual(country_code(""), "")
        self.assertIsNone(country_code("Atlantide"))

    def test_bulk_parser(self):
        from .forms import parse_bulk
        good, errors = parse_bulk("Amina Hassan ; Université de Djibouti ; Djibouti\n\nJean Dupont\t Université de Lyon\t France\nSeul ;;")
        self.assertEqual(errors, [])
        self.assertEqual(good, [("Amina Hassan", "Université de Djibouti", "DJ", "", "participant"), ("Jean Dupont", "Université de Lyon", "FR", "", "participant"), ("Seul", "", "", "", "participant")])
        good, errors = parse_bulk("X ; Y ; Atlantide\n ; Z ; France\nA ; B ; France ; en trop")
        self.assertEqual(good, [])
        self.assertEqual(len(errors), 3)


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class DashboardTests(TestCase):
    PWD = "mot-de-passe-solide-123"

    def setUp(self):
        from django.contrib.auth import get_user_model
        from django.core.cache import cache
        cache.clear()
        self.staff = get_user_model().objects.create_user("chef", password=self.PWD, is_staff=True)
        self.visitor = get_user_model().objects.create_user("lecteur", password=self.PWD)

    def get(self, path):
        return self.client.get(path, secure=True)

    def post(self, path, data=None):
        return self.client.post(path, data or {}, secure=True)

    def login(self):
        self.client.login(username="chef", password=self.PWD)

    def test_dashboard_requires_login(self):
        for path in ("/admin/", "/admin/participants/ajouter/", "/admin/participants/liste/", "/admin/participants/export.csv"):
            response = self.get(path)
            self.assertEqual(response.status_code, 302, path)
            self.assertIn("/admin/connexion/", response["Location"])

    def test_login_page_is_not_indexed_and_wrong_password_is_refused(self):
        self.assertContains(self.get("/admin/connexion/"), "noindex")
        response = self.post("/admin/connexion/", {"username": "chef", "password": "faux"})
        self.assertContains(response, "incorrect")
        self.assertEqual(self.get("/admin/").status_code, 302)

    def test_non_staff_user_cannot_log_in(self):
        response = self.post("/admin/connexion/", {"username": "lecteur", "password": self.PWD})
        self.assertContains(response, "incorrect")
        self.client.login(username="lecteur", password=self.PWD)
        self.assertEqual(self.get("/admin/").status_code, 302)

    def test_login_is_throttled_after_five_failures(self):
        for _ in range(5):
            self.post("/admin/connexion/", {"username": "chef", "password": "faux"})
        response = self.post("/admin/connexion/", {"username": "chef", "password": self.PWD})
        self.assertContains(response, "Trop de tentatives")
        self.assertEqual(self.get("/admin/").status_code, 302)

    def test_login_then_dashboard_lists_everyone(self):
        response = self.post("/admin/connexion/", {"username": "chef", "password": self.PWD})
        self.assertRedirects(response, "/admin/", fetch_redirect_response=False)
        page = html.unescape(self.get("/admin/").content.decode())
        self.assertIn("Ramsès Djidjou-Demasse", page)
        self.assertEqual(page.count("<tr data-s="), 27)

    def test_open_redirect_is_not_possible(self):
        response = self.post("/admin/connexion/", {"username": "chef", "password": self.PWD, "next": "https://evil.example/"})
        self.assertEqual(response["Location"], "/admin/")

    def test_add_edit_delete(self):
        from .models import Participant
        self.login()
        response = self.post("/admin/participants/ajouter/", {"name": "  Amina   Hassan ", "institution": "Université de Djibouti", "country": "DJ"})
        self.assertRedirects(response, "/admin/", fetch_redirect_response=False)
        p = Participant.objects.get(name="Amina Hassan")
        self.assertEqual((p.institution, p.country), ("Université de Djibouti", "DJ"))
        self.assertContains(self.get(f"/admin/participants/{p.pk}/"), "Amina Hassan")
        self.post(f"/admin/participants/{p.pk}/", {"name": "Amina Hassan", "institution": "Université de Lyon", "country": "FR"})
        p.refresh_from_db()
        self.assertEqual((p.institution, p.country), ("Université de Lyon", "FR"))
        self.assertContains(self.get(f"/admin/participants/{p.pk}/supprimer/"), "Supprimer ce participant")
        self.assertTrue(Participant.objects.filter(pk=p.pk).exists())  # un simple affichage ne supprime rien
        self.post(f"/admin/participants/{p.pk}/supprimer/")
        self.assertFalse(Participant.objects.filter(pk=p.pk).exists())

    def test_form_rejects_empty_name_and_unknown_country(self):
        from .models import Participant
        self.login()
        before = Participant.objects.count()
        self.assertContains(self.post("/admin/participants/ajouter/", {"name": " ", "country": "DJ"}), "obligatoire")
        self.post("/admin/participants/ajouter/", {"name": "X", "country": "ZZ"})
        self.assertEqual(Participant.objects.count(), before)

    def test_bulk_add_and_duplicates(self):
        from .models import Participant
        self.login()
        before = Participant.objects.count()
        self.post("/admin/participants/liste/", {"lines": "Amina Hassan ; Université de Djibouti ; Djibouti\nSaid Ismail ; Université Le Havre Normandie ; France\nJean Dupont ; Lyon ; France"})
        self.assertEqual(Participant.objects.count(), before + 2)  # Said Ismail existe déjà
        response = self.post("/admin/participants/liste/", {"lines": "Ok ; A ; France\nKo ; B ; Atlantide"})
        self.assertContains(response, "Rien n’a été ajouté")
        self.assertFalse(Participant.objects.filter(name="Ok").exists())

    def test_csv_export(self):
        self.login()
        response = self.get("/admin/participants/export.csv")
        text = response.content.decode("utf-8-sig")
        self.assertIn("text/csv", response["Content-Type"])
        self.assertEqual(len(text.strip().splitlines()), 28)
        self.assertIn("Ramsès Djidjou-Demasse;IRD — MIVEGEC;;France;Conférencier invité", text)

    def test_logout_requires_post(self):
        self.login()
        self.assertEqual(self.get("/admin/deconnexion/").status_code, 405)
        self.post("/admin/deconnexion/")
        self.assertEqual(self.get("/admin/").status_code, 302)

    def test_csrf_is_enforced(self):
        from django.test import Client
        c = Client(enforce_csrf_checks=True)
        c.login(username="chef", password=self.PWD)
        response = c.post("/admin/participants/ajouter/", {"name": "Pirate"}, secure=True)
        self.assertEqual(response.status_code, 403)


class RolesTests(TestCase):
    def test_interns_and_doctoral_students_are_listed_with_their_status(self):
        from .models import Participant
        self.assertEqual(Participant.objects.filter(role="stagiaire").count(), 4)
        self.assertEqual(Participant.objects.filter(role="doctorant").count(), 7)
        self.assertEqual(Participant.objects.filter(role="chercheur").count(), 6)
        self.assertEqual(Participant.objects.filter(role="invite").count(), 10)
        page = html.unescape(self.client.get("/", secure=True).content.decode())
        section = page[page.index('id="participants" class="page"'):page.index('id="programme" class="page"')]
        self.assertEqual(section.count('data-role="stagiaire"'), 4 + 1)  # 4 lignes + le filtre
        self.assertEqual(section.count('data-role="doctorant"'), 7 + 1)
        for name in ("Kenedid Yacin", "Asma Ahmed", "Mahdi Said", "Fatouma Soubere", "Abdoulrahman Farah"):
            self.assertIn(name, section)
        self.assertIn("Stagiaire (master)", section)
        self.assertIn("Doctorant", section)

    def test_list_is_grouped_by_letter_and_initials_are_shown(self):
        page = html.unescape(self.client.get("/", secure=True).content.decode())
        letters = re.findall(r'<span class="pletter" aria-hidden="true">(.)</span>', page)
        self.assertEqual(letters, sorted(letters))
        self.assertEqual(len(letters), len(set(letters)))
        self.assertIn('class="prow-ini" aria-hidden="true">RD</span>', page)  # Ramsès Djidjou-Demasse
        self.assertIn('class="prow-ini" aria-hidden="true">YS</span>', page)  # « Dr » ignoré dans les initiales

    def test_map_links_every_country_to_the_host_with_an_arc(self):
        page = html.unescape(self.client.get("/", secure=True).content.decode())
        self.assertEqual(page.count('class="world-arc"'), 5)  # 6 pays, dont le pays hôte

    def test_role_codes_from_text(self):
        from .forms import role_code
        self.assertEqual(role_code("Doctorant"), "doctorant")
        self.assertEqual(role_code("intern"), "stagiaire")
        self.assertEqual(role_code("Stagiaires"), "stagiaire")
        self.assertEqual(role_code("Invited speaker"), "invite")
        self.assertEqual(role_code(""), "participant")
        self.assertIsNone(role_code("roi"))


class TwoCountriesTests(TestCase):
    def test_doctoral_students_are_attached_to_france_and_djibouti(self):
        from .models import Participant
        docs = Participant.objects.filter(role="doctorant")
        self.assertEqual(docs.count(), 7)
        for p in docs:
            self.assertEqual((p.country, p.country2), ("FR", "DJ"), p.name)
            self.assertEqual((p.country_fr, p.country_en), ("France / Djibouti", "France / Djibouti"))
        page = html.unescape(self.client.get("/", secure=True).content.decode())
        section = page[page.index('id="participants" class="page"'):page.index('id="programme" class="page"')]
        self.assertEqual(section.count('<em class="chip">France / Djibouti</em>'), 7)

    def test_a_person_with_two_countries_counts_in_each_of_them(self):
        page = html.unescape(self.client.get("/", secure=True).content.decode())
        # France : 5 invités + 7 doctorants ; Djibouti : 6 enseignants-chercheurs + 4 stagiaires + 7 doctorants
        self.assertRegex(page, r'data-q-fr="France"[^>]*>France<b>12</b>')
        self.assertRegex(page, r'data-q-fr="Djibouti"[^>]*>Djibouti<b>17</b>')
        self.assertContains(self.client.get("/", secure=True), '<b>6</b> <span data-en="countries">pays</span>', html=False)

    def test_codes_ignore_duplicates_and_unknown_codes(self):
        from .models import Participant
        self.assertEqual(Participant(name="X", country="FR", country2="FR").codes, ["FR"])
        self.assertEqual(Participant(name="X", country="ZZ", country2="DJ").codes, ["DJ"])
        self.assertEqual(Participant(name="X").country_fr, "")

    def test_bulk_parser_accepts_two_countries(self):
        from .forms import parse_bulk
        good, errors = parse_bulk("Aden Omar ; Université de Nantes ; France / Djibouti ; Doctorant")
        self.assertEqual(errors, [])
        self.assertEqual(good, [("Aden Omar", "Université de Nantes", "FR", "DJ", "doctorant")])
        good, errors = parse_bulk("A ; B ; France / Djibouti / Maroc\nC ; D ; France / Atlantide")
        self.assertEqual(good, [])
        self.assertEqual(len(errors), 2)
