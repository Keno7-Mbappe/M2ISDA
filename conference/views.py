import json
from pathlib import Path

from django.http import HttpResponse
from django.shortcuts import render

from . import content as c


def index(request):
    ctx = {
        "icons": json.loads((Path(__file__).parent / "icons.json").read_text(encoding="utf-8")),
        "speakers": [
            {"name": s[0], "aff": s[1], "country": (s[2], c.COUNTRIES[s[2]]), "img": c.P + s[3] + ".png"}
            for s in c.SPEAKERS
        ],
        "topics": [a[1] for a in c.AXES],
        "days": c.DAYS,
        "milestones": [
            {"iso": m[0], "date": m[1], "year": m[2], "label": m[3], "delay": i * 100, "last": i == len(c.MILESTONES) - 1}
            for i, m in enumerate(c.MILESTONES)
        ],
        "mcf": c.MCF,
        "permanents": [{"name": p[0], "img": c.P + p[1] + ".png"} for p in c.PERMANENTS],
        "doctorants": [{"name": p[0], "aff": p[1], "img": c.P + p[2] + ".png"} for p in c.DOCTORANTS],
        "scientists": [
            {"name": s[0], "aff": s[1], "country": (s[2], c.COUNTRIES[s[2]]), "img": c.P + s[3] + ".png"}
            for s in c.SCIENTISTS
        ],
        "national": [{"abbr": n[0], "name": n[1], "img": c.P + n[2] + ".png"} for n in c.NATIONAL],
        "universities": [{"name": u[0], "img": c.P + u[1] + ".png"} for u in c.UNIVERSITIES],
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


def robots_txt(request):
    lines = ["User-agent: *", "Allow: /", "Disallow: /healthz", "", "Sitemap: https://m2isda.com/sitemap.xml", ""]
    return HttpResponse(chr(10).join(lines), content_type="text/plain")


def sitemap_xml(request):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        "  <url><loc>https://m2isda.com/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>",
        "</urlset>",
        "",
    ]
    return HttpResponse(chr(10).join(lines), content_type="application/xml")
