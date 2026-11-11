from django.db import models
from django.utils import timezone

from .countries import COUNTRIES
from .roles import DEFAULT_ROLE, ROLES


class Participant(models.Model):
    """Une personne de la liste « Participants » (nom, établissement, pays). Géré depuis le tableau de bord."""

    name = models.CharField("Nom", max_length=160)
    institution = models.CharField("Établissement", max_length=200, blank=True)
    institution_en = models.CharField(
        "Établissement (anglais)", max_length=200, blank=True,
        help_text="Facultatif. Laissez vide si le nom est identique en anglais.",
    )
    country = models.CharField("Pays", max_length=2, blank=True)  # code ISO, voir countries.py
    country2 = models.CharField(
        "Deuxième pays", max_length=2, blank=True,
        help_text="Facultatif : pour une personne rattachée à deux pays (par exemple France / Djibouti).",
    )
    role = models.CharField("Statut", max_length=12, default=DEFAULT_ROLE)  # voir roles.py
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        verbose_name = "participant"
        verbose_name_plural = "participants"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def codes(self):
        """Codes des pays rattachés (un ou deux, sans doublon ni code inconnu)."""
        out = []
        for c in (self.country, self.country2):
            if c in COUNTRIES and c not in out:
                out.append(c)
        return out

    @property
    def country_fr(self):
        return " / ".join(COUNTRIES[c][0] for c in self.codes)

    @property
    def country_en(self):
        return " / ".join(COUNTRIES[c][1] for c in self.codes)

    @property
    def role_fr(self):
        return ROLES.get(self.role, ROLES[DEFAULT_ROLE])[0]
