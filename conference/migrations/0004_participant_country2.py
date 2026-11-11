"""Deuxième pays facultatif ; les doctorants sont rattachés à la France et à Djibouti."""
from django.db import migrations, models


def doctorants_france_djibouti(apps, schema_editor):
    Participant = apps.get_model("conference", "Participant")
    Participant.objects.filter(role="doctorant").update(country="FR", country2="DJ")


class Migration(migrations.Migration):
    dependencies = [("conference", "0003_participant_role")]
    operations = [
        migrations.AddField(
            model_name="participant",
            name="country2",
            field=models.CharField(
                blank=True, max_length=2, verbose_name="Deuxième pays",
                help_text="Facultatif : pour une personne rattachée à deux pays (par exemple France / Djibouti).",
            ),
        ),
        migrations.RunPython(doctorants_france_djibouti, migrations.RunPython.noop),
    ]
