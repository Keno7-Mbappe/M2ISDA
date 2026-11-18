"""Liste publique des participants et carte du monde (données lues dans la base)."""
import math
import re
import unicodedata

from django.utils import timezone

from . import worldmap
from .countries import COUNTRIES
from .models import Participant
from .roles import DEFAULT_ROLE, ROLES

MONTHS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
TITLES = {"dr", "pr", "prof", "professeur", "professor"}
HOST = "DJ"
LAT_SPAN = worldmap.HEIGHT / worldmap.CELL * worldmap.STEP  # degrés de latitude couverts par la carte


def fold(text):
    """Minuscules, sans accents ni ponctuation : sert à trier et à chercher."""
    text = unicodedata.normalize("NFKD", text or "").lower()
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def sort_key(name):
    """Ordre alphabétique du nom, sans tenir compte d'un titre éventuel (Dr, Pr…)."""
    words = fold(name).split()
    while words and words[0] in TITLES:
        words.pop(0)
    return " ".join(words)


def _date(dt, months):
    dt = timezone.localtime(dt)
    return dt.day, months[dt.month - 1], dt.year


def _svg_xy(lon, lat):
    """Position d'un point dans le dessin (unités du viewBox)."""
    return ((lon - worldmap.LON0) / 360 * worldmap.WIDTH, (worldmap.LAT0 - lat) / LAT_SPAN * worldmap.HEIGHT)


def _graticule():
    """Méridiens et parallèles tous les 30°."""
    parts = []
    for lon in range(-150, 180, 30):
        parts.append(f"M{_svg_xy(lon, 0)[0]:.0f} 0V{worldmap.HEIGHT}")
    for lat in range(-30, 90, 30):
        parts.append(f"M0 {_svg_xy(0, lat)[1]:.0f}H{worldmap.WIDTH}")
    return "".join(parts)


def _arc(a, b):
    """Courbe douce entre deux points du dessin, bombée vers le haut."""
    (x1, y1), (x2, y2) = a, b
    dist = math.hypot(x2 - x1, y2 - y1)
    cx, cy = (x1 + x2) / 2, min(y1, y2) - dist * 0.28
    return f"M{x1:.1f} {y1:.1f}Q{cx:.1f} {cy:.1f} {x2:.1f} {y2:.1f}"


def participants_context():
    people = sorted(Participant.objects.all(), key=lambda p: (sort_key(p.name), p.pk))
    rows, by_country, role_n = [], {}, {}
    for p in people:
        codes = p.codes
        role = p.role if p.role in ROLES else DEFAULT_ROLE
        role_n[role] = role_n.get(role, 0) + 1
        initials = "".join(w[0] for w in [w for w in p.name.split() if fold(w) not in TITLES][:2]).upper() or "?"
        rows.append({
            "name": p.name,
            "ini": initials,
            "letter": (sort_key(p.name)[:1] or "#").upper(),
            "inst": (p.institution, p.institution_en or p.institution),
            "country": (p.country_fr, p.country_en) if codes else None,
            "role": role,
            "role_label": ROLES[role][:2],
            "search": fold(" ".join([p.name, p.institution, p.institution_en, p.country_fr, p.country_en,
                                     *codes, ROLES[role][0], ROLES[role][1]])),
        })
        for code in codes:  # une personne rattachée à deux pays compte dans chacun
            info = COUNTRIES[code]
            slot = by_country.setdefault(code, {"code": code, "fr": info[0], "en": info[1], "n": 0, "lat": info[2], "lon": info[3]})
            slot["n"] += 1

    groups = []  # un groupe par initiale
    for r in rows:
        if not groups or groups[-1]["letter"] != r["letter"]:
            groups.append({"letter": r["letter"], "rows": []})
        groups[-1]["rows"].append(r)

    if HOST not in by_country and HOST in COUNTRIES:  # le pays hôte figure toujours sur la carte
        info = COUNTRIES[HOST]
        by_country[HOST] = {"code": HOST, "fr": info[0], "en": info[1], "n": 0, "lat": info[2], "lon": info[3]}
    host_pt = _svg_xy(by_country[HOST]["lon"], by_country[HOST]["lat"]) if HOST in by_country else None
    pins, arcs = [], []
    for c in by_country.values():
        x, y = _svg_xy(c["lon"], c["lat"])
        px, py = min(max(x / worldmap.WIDTH * 100, 1), 99), min(max(y / worldmap.HEIGHT * 100, 2), 98)
        # textes (pas de virgule décimale dans le CSS)
        pins.append({**c, "host": c["code"] == HOST, "x": f"{px:.2f}", "y": f"{py:.2f}", "size": f"{11 + 3 * math.sqrt(c['n']):.1f}"})
        if host_pt and c["code"] != HOST and c["n"]:
            arcs.append(_arc((x, y), host_pt))
    pins.sort(key=lambda c: (-c["n"], fold(c["fr"])))

    on = "".join(worldmap.DOTS[c] for c in by_country if c in worldmap.DOTS)
    rest = "".join(d for code, d in worldmap.DOTS.items() if code not in by_country)

    updated = max((p.updated_at for p in people), default=None)
    if updated:
        d, m, y = _date(updated, MONTHS_FR)
        d2, m2, y2 = _date(updated, MONTHS_EN)
        upd = (f"{d}{'er' if d == 1 else ''} {m} {y}", f"{m2} {d2}, {y2}")
    else:
        upd = None
    return {
        "rows": rows,
        "groups": groups,
        "total": len(rows),
        "roles": [{"code": k, "n": role_n[k], "fr": ROLES[k][2], "en": ROLES[k][3]} for k in ROLES if role_n.get(k)],
        "pins": pins,
        "arcs": arcs,
        "n_countries": len([c for c in pins if c["n"]]),
        # « DPCR — Directeur général » et « DPCR — Directeur des opérations » comptent pour un seul établissement
        "n_inst": len({r["inst"][0].split(" — ")[0].strip().lower() for r in rows if r["inst"][0].strip()}),
        "map_on": on,
        "map_rest": rest,
        "map_grid": _graticule(),
        "map_w": worldmap.WIDTH,
        "map_h": worldmap.HEIGHT,
        "map_dot": f"{worldmap.CELL * 0.56:.2f}",
        "updated": upd,
    }
