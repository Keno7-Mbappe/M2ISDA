"""Contenu du site M2ISDA 2027. Chaque texte traduisible est un couple (fr, en)."""
import re

P = "conference/img/p/"

SPEAKERS = [
    ("Ramsès Djidjou-Demasse", ("IRD — MIVEGEC", "IRD — MIVEGEC"), "France", "djidjou"),
    ("Nathalie Verdière", ("Université Le Havre Normandie", "Le Havre Normandie University"), "France", "verdiere"),
    ("M. A. Aziz-Alaoui", ("LMAH — Le Havre Normandie", "LMAH — Le Havre Normandie"), "France", "aziz"),
    ("Hacène Djellout", ("Université Clermont Auvergne", "Clermont Auvergne University"), "France", "djellout"),
    ("Raluca Eftimie", ("Université Marie et Louis Pasteur", "Marie & Louis Pasteur University"), "France", "eftimie"),
    ("El Azroul", ("Université Sidi Mohamed Ben Abdellah", "Sidi Mohamed Ben Abdellah University"), "Maroc", "elazroul"),
    ("Clément Manga", ("Université Assane Seck de Ziguinchor", "Assane Seck University of Ziguinchor"), "Sénégal", "manga"),
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
        "date": ("Mardi 19 janvier 2027", "Tuesday 19 January 2027"),
        "title": ("Ouverture et conférences plénières", "Opening and plenary lectures"),
        "slots": [
            (("Matin", "Morning"), [("Cérémonie d’ouverture, puis premières conférences plénières des invités", "Opening ceremony, then the first invited plenary lectures")]),
            (("Après-midi", "Afternoon"), [
                ("Session 1 — Modélisation épidémiologique et santé publique", "Session 1 — Epidemiological modelling and public health"),
                ("Session 2 — Statistique, biostatistique et sciences des données", "Session 2 — Statistics, biostatistics and data science"),
            ]),
        ],
    },
    {
        "wd": ("Mercredi", "Wednesday"), "num": "20",
        "date": ("Mercredi 20 janvier 2027", "Wednesday 20 January 2027"),
        "title": ("Conférences, panel et excursion", "Lectures, panel and excursion"),
        "slots": [
            (("Matin", "Morning"), [
                ("Conférences plénières", "Plenary lectures"),
                ("Panel « Modélisation et décision publique à Djibouti », avec les institutions nationales", "Panel “Modelling and public decision-making in Djibouti”, with the national institutions"),
            ]),
            (("Après-midi", "Afternoon"), [("Excursion", "Excursion")]),
        ],
    },
    {
        "wd": ("Jeudi", "Thursday"), "num": "21",
        "date": ("Jeudi 21 janvier 2027", "Thursday 21 January 2027"),
        "title": ("Présentations, clôture et dîner de gala", "Presentations, closing and gala dinner"),
        "slots": [
            (("Matin", "Morning"), [
                ("Session 3 — Optimisation et recherche opérationnelle", "Session 3 — Optimization and operations research"),
                ("Session 4 — Écosystèmes, climat et environnement", "Session 4 — Ecosystems, climate and environment"),
            ]),
            (("Après-midi", "Afternoon"), [
                ("Session 5 — Systèmes portuaires et logistiques", "Session 5 — Port and logistics systems"),
                ("Session posters des doctorants", "Doctoral poster session"),
                ("Synthèse et clôture", "Summary and closing"),
            ]),
            (("Soir", "Evening"), [("Dîner de gala", "Gala dinner")]),
        ],
    },
]

MILESTONES = [
    ("2026-12-31", ("31 décembre", "31 December"), "2026", ("Clôture des inscriptions", "Registration closes")),
    ("2027-01-05", ("5 janvier", "5 January"), "2027", ("Date limite d’envoi des résumés", "Abstract submission deadline")),
    ("2027-01-10", ("10 janvier", "10 January"), "2027", ("Notification aux auteurs", "Notification to authors")),
    ("2027-01-19", ("19 — 21 janvier", "19 — 21 January"), "2027", ("Conférence à Djibouti", "Conference in Djibouti")),
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
    ("Université de Djibouti", "University of Djibouti", "ud"), ("Le Havre Normandie", "Le Havre Normandie", "lehavre"),
    ("Clermont Auvergne", "Clermont Auvergne", "uca"), ("Marie et Louis Pasteur", "Marie & Louis Pasteur", "umlp"),
    ("Adama Science and Technology", "Adama Science and Technology", "adama"),
    ("Amoud University", "Amoud University", "amoud"), ("Mogadishu University", "Mogadishu University", "mogadishu"),
]

LEAD = {
    "fr": "La deuxième édition de M2ISDA réunit à Djibouti des chercheurs en mathématiques appliquées, en statistique et en sciences des données pour présenter leurs travaux récents, partager leurs idées et développer de nouvelles méthodes.",
    "en": "The second edition of M2ISDA brings together researchers in applied mathematics, statistics and data science in Djibouti to present their recent work, share ideas and develop new methods.",
}

TEX = r"""% M2ISDA 2027 — modèle de résumé
\documentclass[11pt,a4paper]{article}
\usepackage[margin=2.5cm]{geometry}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[french]{babel}
\usepackage{amsmath,amssymb}

\title{Titre du résumé}
\author{Prénom Nom\textsuperscript{1}, Prénom Nom\textsuperscript{2}\\
  \small\textsuperscript{1}Affiliation, Pays \quad
  \textsuperscript{2}Affiliation, Pays}
\date{}

\begin{document}
\maketitle
\noindent\textbf{Axe thématique :} à préciser\\
\textbf{Préférence :} communication orale / poster

\section*{Résumé}
Texte du résumé (une page au maximum, références comprises).

\noindent\textbf{Mots-clés :} mot 1, mot 2, mot 3

\begin{thebibliography}{9}
\bibitem{ref1} Auteur, \emph{Titre}, Revue, année.
\end{thebibliography}
\end{document}"""

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
