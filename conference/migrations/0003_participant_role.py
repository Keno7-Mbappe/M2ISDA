"""Statut des participants (invité, enseignant-chercheur, doctorant, stagiaire…) + ajout des quatre stagiaires du master."""
from django.db import migrations, models
from django.utils import timezone

INVITES = [
    "Ramsès Djidjou-Demasse", "Nathalie Verdière", "M. A. Aziz-Alaoui", "Hacène Djellout", "Raluca Eftimie",
    "El Houssine Azroul", "Clément Manga", "Legesse Lemecha Obsu", "Abdisalam Hassan", "Daud Ali Aser",
]
CHERCHEURS = [
    "Dr Yahyeh Souleiman", "Dr Liban Ismail", "Dr Souleiman Omar", "Dr Doualeh Ali", "Dr Souleiman Isman Guedi", "Dr Hassan Ali Barkad",
]
DOCTORANTS = ["Said Ismail", "Gouled Souleiman", "Ali Mohamed", "Saida Ballah", "Hakim Amer", "Kadir Ali", "Abdoulrahman Farah"]
STAGIAIRES = ["Kenedid Yacin", "Asma Ahmed", "Mahdi Said", "Fatouma Soubere"]


def fill_roles(apps, schema_editor):
    Participant = apps.get_model("conference", "Participant")
    for role, names in (("invite", INVITES), ("chercheur", CHERCHEURS), ("doctorant", DOCTORANTS)):
        Participant.objects.filter(name__in=names).update(role=role)
    now = timezone.now()
    have = set(Participant.objects.values_list("name", flat=True))
    Participant.objects.bulk_create([
        Participant(name=n, institution="Université de Djibouti", institution_en="University of Djibouti", country="DJ",
                    role="stagiaire", created_at=now, updated_at=now)
        for n in STAGIAIRES if n not in have
    ])


class Migration(migrations.Migration):
    dependencies = [("conference", "0002_participants_initiaux")]
    operations = [
        migrations.AddField(
            model_name="participant",
            name="role",
            field=models.CharField(default="participant", max_length=12, verbose_name="Statut"),
        ),
        migrations.RunPython(fill_roles, migrations.RunPython.noop),
    ]
