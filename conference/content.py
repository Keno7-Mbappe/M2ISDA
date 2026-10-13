"""Contenu du site M2ISDA 2027. Chaque texte traduisible est un couple (fr, en)."""
import re
from pathlib import Path

P = "conference/img/p/"

SPEAKERS = [
    ("Ramsès Djidjou-Demasse", ("IRD — MIVEGEC", "IRD — MIVEGEC"), "France", "djidjou"),
    ("Nathalie Verdière", ("Université Le Havre Normandie", "Le Havre Normandie University"), "France", "verdiere"),
    ("M. A. Aziz-Alaoui", ("LMAH — Le Havre Normandie", "LMAH — Le Havre Normandie"), "France", "aziz"),
    ("Hacène Djellout", ("Université Clermont Auvergne", "Clermont Auvergne University"), "France", "djellout"),
    ("Raluca Eftimie", ("Université Marie et Louis Pasteur", "Marie & Louis Pasteur University"), "France", "eftimie"),
    ("El Azroul", ("Université Sidi Mohamed Ben Abdellah", "Sidi Mohamed Ben Abdellah University"), "Maroc", "elazroul"),
    ("Clément Manga", ("Université Assane Seck de Ziguinchor", "Assane Seck Ziguinchor University"), "Sénégal", "manga"),
    ("Legesse Lemecha Obsu", ("Adama Science and Technology University",) * 2, "Éthiopie", "lemecha"),
    ("Abdisalam Hassan", ("Université Amoud", "Amoud University"), "Somalie", "abdisalam"),
    ("Daud Ali Aser", ("Mogadishu University",) * 2, "Somalie", "daud"),
]

COUNTRIES = {
    "France": "France", "Maroc": "Morocco", "Sénégal": "Senegal", "Éthiopie": "Ethiopia",
    "Somalie": "Somalia", "Djibouti": "Djibouti",
}

AXES = [
    ("I", ("Modélisation épidémiologique et santé publique", "Epidemiological modelling and public health"), "dI/dt = βSI − γI", "SIR"),
    ("II", ("Statistique, biostatistique et science des données", "Statistics, biostatistics and data science"), "θ̂ = argmax ℓ(θ | x)", "EMV"),
    ("III", ("Optimisation et recherche opérationnelle", "Optimization and operations research"), "min f(x)  s.c.  Ax ≤ b", "PL"),
    ("IV", ("Modélisation des écosystèmes et écologie", "Ecosystem modelling and ecology"), "dN/dt = rN (1 − N/K)", "Verhulst"),
    ("V", ("Modèles climatiques et environnementaux", "Climate and environmental models"), "∂T/∂t = κ ∇²T + Q", "Diffusion"),
    ("VI", ("Modélisation des systèmes portuaires et logistiques", "Port and logistics systems modelling"), "ρ = λ / (cμ) < 1", "M/M/c"),
    ("VII", ("Mathématiques appliquées à l’industrie et à l’ingénierie", "Applied mathematics for industry and engineering"), "−∇·(k ∇u) = f  dans Ω", "EDP"),
    ("VIII", ("Aide à la décision et systèmes d’aide à la décision", "Decision support systems"), "a* = argmax 𝔼[U(a, θ)]", "Bayes"),
]

DAYS = [
    {
        "wd": ("Mardi", "Tuesday"), "num": "19",
        "tag": ("Mardi 19 janvier", "Tuesday 19 January"),
        "title": ("Ouverture et conférences plénières", "Opening and plenary lectures"),
        "slots": [
            (("Matin", "Morning"), ("Cérémonie d’ouverture, puis premières conférences plénières des invités", "Opening ceremony, then the first invited plenary lectures")),
            (("Après-midi", "Afternoon"), ("Session 1 — Modélisation épidémiologique et santé publique · Session 2 — Statistique, biostatistique et sciences des données", "Session 1 — Epidemiological modelling and public health · Session 2 — Statistics, biostatistics and data science")),
        ],
    },
    {
        "wd": ("Mercredi", "Wednesday"), "num": "20",
        "tag": ("Mercredi 20 janvier", "Wednesday 20 January"),
        "title": ("Conférences, panel et excursion", "Lectures, panel and excursion"),
        "slots": [
            (("Matin", "Morning"), ("Conférences plénières · Panel « Modélisation et décision publique à Djibouti », avec les institutions nationales", "Plenary lectures · Panel “Modelling and public decision-making in Djibouti”, with the national institutions")),
            (("Après-midi", "Afternoon"), ("Excursion", "Excursion")),
        ],
    },
    {
        "wd": ("Jeudi", "Thursday"), "num": "21",
        "tag": ("Jeudi 21 janvier", "Thursday 21 January"),
        "title": ("Présentations, clôture et dîner de gala", "Presentations, closing and gala dinner"),
        "slots": [
            (("Matin", "Morning"), ("Session 3 — Optimisation et recherche opérationnelle · Session 4 — Écosystèmes, climat et environnement", "Session 3 — Optimization and operations research · Session 4 — Ecosystems, climate and environment")),
            (("Après-midi", "Afternoon"), ("Session 5 — Systèmes portuaires et logistiques · Session posters des doctorants · Synthèse et clôture", "Session 5 — Port and logistics systems · Doctoral poster session · Summary and closing")),
            (("Soir", "Evening"), ("Dîner de gala", "Gala dinner")),
        ],
    },
]

MILESTONES = [
    ("2026-12-31", ("31 décembre", "31 December"), "2026", ("Clôture des inscriptions", "Registration closes")),
    ("2027-01-05", ("5 janvier", "5 January"), "2027", ("Date limite d’envoi des résumés", "Abstract submission deadline")),
    ("2027-01-10", ("10 janvier", "10 January"), "2027", ("Notification aux auteurs", "Notification to authors")),
    ("2027-01-19", ("19 – 21 janvier", "19 – 21 January"), "2027", ("Conférence à Djibouti", "Conference in Djibouti")),
]

MCF = ("Maître de conférences", "Associate professor")
PERMANENTS = [("Dr Yahyeh Souleiman", "yahyeh"), ("Dr Liban Ismail", "liban"), ("Dr Souleiman Omar", "souleiman"), ("Dr Doualeh Ali", "doualeh")]
DOCTORANTS = [
    ("Said Ismail", "Le Havre Normandie", "said"), ("Gouled Souleiman", "Le Havre Normandie", "gouled"),
    ("Ali Mohamed", "La Rochelle", "alim"), ("Saida Ballah", "Nantes", "saida"),
    ("Hakim Amer", "Toulon", "hakim"), ("Kadir Ali", "Marie et Louis Pasteur", "kadir"),
]
_UD = ("Maître de conférences, Université de Djibouti", "Associate Professor, University of Djibouti")
SCIENTISTS = [
    ("Dr Liban Ismail", _UD, "Djibouti", "liban"),
    ("Dr Yahyeh Souleiman", _UD, "Djibouti", "yahyeh"),
    ("Dr Souleiman Omar", _UD, "Djibouti", "souleiman"),
    ("Dr Doualeh Ali", _UD, "Djibouti", "doualeh"),
    ("Dr Abdisalam Hassan", ("Maître de conférences, Université Amoud", "Associate Professor, Amoud University"), "Somalie", "abdisalam"),
    ("Pr Nathalie Verdière", ("Université Le Havre Normandie", "Le Havre Normandie University"), "France", "verdiere"),
    ("Pr Hacène Djellout", ("Université Clermont Auvergne", "Clermont Auvergne University"), "France", "djellout"),
    ("Pr Raluca Eftimie", ("Université Marie et Louis Pasteur", "Marie & Louis Pasteur University"), "France", "eftimie"),
    ("Pr Legesse Lemecha Obsu", ("Adama Science and Technology University",) * 2, "Éthiopie", "lemecha"),
]

NATIONAL = [
    ("INSTAD", ("Institut national de la statistique de Djibouti", "National Institute of Statistics of Djibouti"), "instad"),
    ("INSPD", ("Institut national de santé publique de Djibouti", "National Institute of Public Health of Djibouti"), "inspd"),
    ("CHU de Djibouti", ("Centre hospitalier universitaire", "University Hospital"), "chu"),
    ("Hôpital militaire", ("Service de santé des armées — CSSA", "Army Health Service — CSSA"), "cssa"),
    ("DPCS", ("Djibouti Port Community Systems",) * 2, "dpcs"),
    ("SGTD", ("Terminal à conteneurs de Doraleh", "Doraleh Container Terminal"), "sgtd"),
    ("DPCR", ("Djibouti Ports Corridor Road",) * 2, "dpcr"),
]
UNIVERSITIES = [
    ("Université de Djibouti", "ud"), ("Le Havre Normandie", "lehavre"), ("Clermont Auvergne", "uca"),
    ("Marie et Louis Pasteur", "umlp"), ("Adama Science and Technology", "adama"),
    ("Amoud University", "amoud"), ("Mogadishu University", "mogadishu"),
]

TEX = (Path(__file__).parent / "static/conference/downloads/M2ISDA_2027_modele_resume.tex").read_text(encoding="utf-8").rstrip(chr(10))

_TOKEN = re.compile(r"(\\[a-zA-Z]+|\{[^{}]*\}|\[[^\]]*\])")


def tex_lines():
    """Colorisation LaTeX côté serveur : liste de lignes, chacune une liste (classe, texte)."""
    out = []
    for i, line in enumerate(TEX.split("\n"), 1):
        if line.lstrip().startswith("%"):
            parts = [("com", line or " ")]
        else:
            parts, last = [], 0
            for m in _TOKEN.finditer(line):
                if m.start() > last:
                    parts.append(("txt", line[last:m.start()]))
                s = m.group(0)
                parts.append(("cmd" if s[0] == "\\" else "brace" if s[0] == "{" else "brk", s))
                last = m.end()
            if last < len(line):
                parts.append(("txt", line[last:]))
            if not parts:
                parts = [("txt", " ")]
        out.append({"no": i, "parts": parts})
    return out
