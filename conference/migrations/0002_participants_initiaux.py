"""Liste initiale des participants (celle qui était affichée sur le site avant le tableau de bord)."""
from datetime import datetime, timezone

from django.db import migrations

# (nom, établissement, établissement en anglais, code pays)
SEED = [
    ('Ramsès Djidjou-Demasse', 'IRD — MIVEGEC', '', 'FR'),
    ('Nathalie Verdière', 'Université Le Havre Normandie', 'Le Havre Normandie University', 'FR'),
    ('M. A. Aziz-Alaoui', 'LMAH — Le Havre Normandie', '', 'FR'),
    ('Hacène Djellout', 'Université Clermont Auvergne', 'Clermont Auvergne University', 'FR'),
    ('Raluca Eftimie', 'Université Marie et Louis Pasteur', 'Marie & Louis Pasteur University', 'FR'),
    ('El Houssine Azroul', 'Université Sidi Mohamed Ben Abdellah', 'Sidi Mohamed Ben Abdellah University', 'MA'),
    ('Clément Manga', 'Université Assane Seck de Ziguinchor', 'Assane Seck Ziguinchor University', 'SN'),
    ('Legesse Lemecha Obsu', 'Adama Science and Technology University', '', 'ET'),
    ('Abdisalam Hassan', 'Université Amoud', 'Amoud University', 'SO'),
    ('Daud Ali Aser', 'Mogadishu University', '', 'SO'),
    ('Dr Yahyeh Souleiman', 'Université de Djibouti', 'University of Djibouti', 'DJ'),
    ('Dr Liban Ismail', 'Université de Djibouti', 'University of Djibouti', 'DJ'),
    ('Dr Souleiman Omar', 'Université de Djibouti', 'University of Djibouti', 'DJ'),
    ('Dr Doualeh Ali', 'Université de Djibouti', 'University of Djibouti', 'DJ'),
    ('Dr Souleiman Isman Guedi', 'Université de Djibouti', 'University of Djibouti', 'DJ'),
    ('Dr Hassan Ali Barkad', 'Université de Djibouti', 'University of Djibouti', 'DJ'),
    ('Said Ismail', 'Université Le Havre Normandie', 'Le Havre Normandie University', 'FR'),
    ('Gouled Souleiman', 'Université Le Havre Normandie', 'Le Havre Normandie University', 'FR'),
    ('Ali Mohamed', 'La Rochelle Université', 'La Rochelle University', 'FR'),
    ('Saida Ballah', 'Nantes Université', 'Nantes University', 'FR'),
    ('Hakim Amer', 'Université de Toulon', 'University of Toulon', 'FR'),
    ('Kadir Ali', 'Université Marie et Louis Pasteur', 'Marie & Louis Pasteur University', 'FR'),
    ('Abdoulrahman Farah', '', '', ''),
]
UPDATED = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)  # date de la dernière mise à jour affichée jusqu'ici


def seed(apps, schema_editor):
    Participant = apps.get_model("conference", "Participant")
    if Participant.objects.exists():
        return
    Participant.objects.bulk_create([
        Participant(name=n, institution=i, institution_en=e, country=c, created_at=UPDATED, updated_at=UPDATED)
        for n, i, e, c in SEED
    ])


class Migration(migrations.Migration):
    dependencies = [("conference", "0001_participant")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
