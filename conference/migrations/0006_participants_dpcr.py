"""Ajout de deux responsables du DPCR (Djibouti). Leur fonction figure dans la colonne « établissement »."""
from django.db import migrations
from django.utils import timezone

# (nom affiché, établissement, établissement en anglais, pays)
NOUVEAUX = [
    ("Warsama Mouhoumed Bouh", "DPCR — Directeur général", "DPCR — Director General", "DJ"),
    ("Abdourahman Haroun", "DPCR — Directeur des opérations", "DPCR — Director of Operations", "DJ"),
]


def add_people(apps, schema_editor):
    Participant = apps.get_model("conference", "Participant")
    now = timezone.now()
    have = set(Participant.objects.values_list("name", flat=True))
    Participant.objects.bulk_create([
        Participant(name=n, institution=i, institution_en=e, country=c, role="participant", created_at=now, updated_at=now)
        for n, i, e, c in NOUVEAUX if n not in have
    ])


class Migration(migrations.Migration):
    dependencies = [("conference", "0005_participants_liste_complete")]
    operations = [migrations.RunPython(add_people, migrations.RunPython.noop)]
