from django import forms

from .countries import COUNTRIES
from .models import Participant
from .participants import fold
from .roles import DEFAULT_ROLE, ROLES

COUNTRY_CHOICES = [("", "— Aucun pays —")] + [(k, v[0]) for k, v in sorted(COUNTRIES.items(), key=lambda kv: fold(kv[1][0]))]


ROLE_CHOICES = [(k, v[0]) for k, v in ROLES.items()]


class ParticipantForm(forms.ModelForm):
    country = forms.ChoiceField(label="Pays", choices=COUNTRY_CHOICES, required=False)
    country2 = forms.ChoiceField(
        label="Deuxième pays", choices=COUNTRY_CHOICES, required=False,
        help_text="Facultatif : pour une personne rattachée à deux pays (par exemple France / Djibouti).",
    )
    role = forms.ChoiceField(label="Statut", choices=ROLE_CHOICES, initial=DEFAULT_ROLE, required=False)

    class Meta:
        model = Participant
        fields = ["name", "role", "institution", "institution_en", "country", "country2"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Prénom Nom", "autofocus": True}),
            "institution": forms.TextInput(attrs={"placeholder": "Université, laboratoire, organisme…"}),
            "institution_en": forms.TextInput(attrs={"placeholder": "University, laboratory, organisation…"}),
        }

    def clean_role(self):
        return self.cleaned_data["role"] or DEFAULT_ROLE

    def clean_name(self):
        return " ".join(self.cleaned_data["name"].split())

    def clean_institution(self):
        return " ".join(self.cleaned_data["institution"].split())

    def clean_institution_en(self):
        return " ".join(self.cleaned_data["institution_en"].split())


class BulkForm(forms.Form):
    lines = forms.CharField(
        label="Liste",
        widget=forms.Textarea(attrs={"rows": 12, "placeholder": "Amina Hassan ; Université de Djibouti ; Djibouti ; Doctorant\nJean Dupont ; Université de Lyon ; France ; Participant"}),
    )


def country_code(text):
    """Code ISO à partir d'un nom (français ou anglais) ou d'un code. Chaîne vide si absent, None si inconnu."""
    text = (text or "").strip()
    if not text:
        return ""
    if len(text) == 2 and text.upper() in COUNTRIES:
        return text.upper()
    key = fold(text)
    for code, (fr, en, _lat, _lon) in COUNTRIES.items():
        if key in (fold(fr), fold(en)):
            return code
    ALIASES = {"usa": "US", "etats unis d amerique": "US", "uk": "GB", "angleterre": "GB", "england": "GB", "ivory coast": "CI",
               "cote d ivoire": "CI", "republique democratique du congo": "CD", "rdc": "CD", "drc": "CD", "tchequie": "CZ",
               "republique tcheque": "CZ", "czech republic": "CZ", "turkey": "TR", "turquie": "TR", "swaziland": "SZ",
               "emirats arabes unis": "AE", "uae": "AE"}
    return ALIASES.get(key)


def role_code(text):
    """Code de statut à partir de son nom (français ou anglais, singulier ou pluriel). Défaut si vide, None si inconnu."""
    key = fold(text)
    if not key:
        return DEFAULT_ROLE
    for code, labels in ROLES.items():
        if key == code or key in {fold(x) for x in labels}:
            return code
    ALIASES = {"stagiaire": "stagiaire", "stagiaires": "stagiaire", "intern": "stagiaire", "etudiant": "stagiaire", "etudiant en master": "stagiaire",
               "master": "stagiaire", "phd": "doctorant", "doctorante": "doctorant", "invite": "invite", "speaker": "invite", "enseignant": "chercheur"}
    return ALIASES.get(key)


def parse_bulk(text):
    """Une personne par ligne : Nom ; Établissement ; Pays ; Statut  (séparateur ; | ou tabulation). Retourne (lignes valides, erreurs). Le pays peut être « France / Djibouti »."""
    good, errors = [], []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        sep = "\t" if "\t" in line else ("|" if "|" in line and ";" not in line else ";")
        parts = [p.strip() for p in line.split(sep)]
        name = " ".join(parts[0].split())
        if not name:
            errors.append(f"Ligne {n} : le nom est vide.")
            continue
        if len(parts) > 4:
            errors.append(f"Ligne {n} : trop de colonnes (attendu : Nom ; Établissement ; Pays ; Statut) — « {line[:60]} ».")
            continue
        inst = " ".join(parts[1].split()) if len(parts) > 1 else ""
        names = [x for x in (parts[2].split("/") if len(parts) > 2 else []) if x.strip()][:3]
        codes = [country_code(x) for x in names]
        if len(names) > 2:
            errors.append(f"Ligne {n} : deux pays au plus (« {parts[2]} »).")
            continue
        if None in codes:
            errors.append(f"Ligne {n} : pays inconnu « {parts[2]} » (écrivez-le en français ou en anglais ; deux pays se séparent par « / »).")
            continue
        code, code2 = (codes + ["", ""])[:2]
        role = role_code(parts[3]) if len(parts) > 3 else DEFAULT_ROLE
        if role is None:
            errors.append(f"Ligne {n} : statut inconnu « {parts[3]} » (invité, enseignant-chercheur, doctorant, stagiaire ou participant).")
            continue
        if len(name) > 160 or len(inst) > 200:
            errors.append(f"Ligne {n} : texte trop long.")
            continue
        good.append((name, inst, code, code2, role))
    return good, errors
