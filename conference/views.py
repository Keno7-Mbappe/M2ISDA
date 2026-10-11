from django.http import HttpResponse
from django.shortcuts import render

from . import content as c


def index(request):
    ctx = {
        "speakers": [
            {"n": f"{i:02d}", "name": s[0], "aff": s[1], "country": (s[2], c.COUNTRIES[s[2]]), "img": c.P + s[3] + ".png"}
            for i, s in enumerate(c.SPEAKERS, 1)
        ],
        "axes": [{"num": a[0], "title": a[1], "eq": a[2], "tag": a[3], "delay": (i % 4) * 90} for i, a in enumerate(c.AXES)],
        "days": c.DAYS,
        "milestones": [
            {"iso": m[0], "date": m[1], "year": m[2], "label": m[3], "delay": i * 120, "last": i == len(c.MILESTONES) - 1}
            for i, m in enumerate(c.MILESTONES)
        ],
        "mcf": c.MCF,
        "permanents": [{"name": p[0], "img": c.P + p[1] + ".png"} for p in c.PERMANENTS],
        "doctorants": [{"name": p[0], "aff": p[1], "img": c.P + p[2] + ".png"} for p in c.DOCTORANTS],
        "scientists": [
            {"name": s[0], "aff": s[1], "country": (s[2], c.COUNTRIES[s[2]]), "img": c.P + s[3] + ".png"}
            for s in c.SCIENTISTS
        ],
        "national": [{"abbr": n[0], "name": n[1], "img": c.P + n[2] + ".png", "delay": (i % 4) * 80} for i, n in enumerate(c.NATIONAL)],
        "universities": [{"fr": u[0], "en": u[1], "img": c.P + u[2] + ".png", "delay": (i % 6) * 70} for i, u in enumerate(c.UNIVERSITIES)],
        "lead_words": c.lead_words(),
        "lead_fr": c.LEAD["fr"][0],
        "lead_en": c.LEAD["en"][0],
        "accent_fr": " ".join(c.LEAD["fr"][1]),
        "accent_en": " ".join(c.LEAD["en"][1]),
        "marquee_axes": [a[1] for a in c.AXES],
        "marquee_partners": [n[0] for n in c.NATIONAL] + [u[0] for u in c.UNIVERSITIES],
        "tex_lines": c.tex_lines(),
        "tex": c.TEX,
    }
    return render(request, "conference/index.html", ctx)


def healthz(request):
    return HttpResponse("ok", content_type="text/plain")


def tex_template(request):
    response = HttpResponse(c.TEX + "\n", content_type="application/x-tex; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="M2ISDA2027_resume.tex"'
    return response
