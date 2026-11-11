"""Statuts des participants : code -> (singulier FR, singulier EN, pluriel FR, pluriel EN). L'ordre est celui des filtres du site."""
ROLES = {
    "invite": ("Conférencier invité", "Invited speaker", "Conférenciers invités", "Invited speakers"),
    "chercheur": ("Enseignant-chercheur", "Academic staff", "Enseignants-chercheurs", "Academic staff"),
    "doctorant": ("Doctorant", "Doctoral student", "Doctorants", "Doctoral students"),
    "stagiaire": ("Stagiaire (master)", "Intern (Master’s)", "Stagiaires (master)", "Interns (Master’s)"),
    "participant": ("Participant", "Participant", "Autres participants", "Other participants"),
}
DEFAULT_ROLE = "participant"
