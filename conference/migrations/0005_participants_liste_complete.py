"""Liste complète des participants (fichier Liste_participants_M2ISDA_2027.xlsx) : ajout des 9 personnes qui manquaient
et renseignement de l'établissement d'Abdoulrahman Farah. Les statuts ne figurant pas dans le fichier, les nouveaux
venus sont enregistrés comme « Participant »."""
from django.db import migrations
from django.utils import timezone

# (nom affiché, établissement, établissement en anglais, pays)
NOUVEAUX = [
    ("Abdikani Mohamed Aden", "Université Amoud", "Amoud University", "SO"),
    ("Ahmed Awale Ahmed", "Université Amoud", "Amoud University", "SO"),
    ("Abdulkadir Abdi Ali", "Université Amoud", "Amoud University", "SO"),
    ("Hamze G. Dahir", "Université Amoud", "Amoud University", "SO"),
    ("Abdisalam Yusuf Duale", "Université Amoud", "Amoud University", "SO"),
    ("Joseph Ngatchou-Wandji", "Université de Lorraine", "University of Lorraine", "FR"),
    ("Abdirahim Mohamed Muhumed", "Université Amoud", "Amoud University", "SO"),
    ("Mustafe Aden Muhumed", "Université de Hargeisa", "University of Hargeisa", "SO"),
    ("Bishar Elmi Yey", "Université Amoud", "Amoud University", "SO"),
]


def add_people(apps, schema_editor):
    Participant = apps.get_model("conference", "Participant")
    now = timezone.now()
    have = set(Participant.objects.values_list("name", flat=True))
    Participant.objects.bulk_create([
        Participant(name=n, institution=i, institution_en=e, country=c, role="participant", created_at=now, updated_at=now)
        for n, i, e, c in NOUVEAUX if n not in have
    ])
    Participant.objects.filter(name="Abdoulrahman Farah", institution="").update(
        institution="Université de Lorraine", institution_en="University of Lorraine", updated_at=now)


class Migration(migrations.Migration):
    dependencies = [("conference", "0004_participant_country2")]
    operations = [migrations.RunPython(add_people, migrations.RunPython.noop)]
