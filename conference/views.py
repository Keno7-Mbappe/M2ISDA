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
        "days": c.DAYS,
        "milestones": [
            {"iso": m[0], "date": m[1], "year": m[2], "label": m[3], "delay": i * 100, "last": i == len(c.MILESTONES) - 1}
            for i, m in enumerate(c.MILESTONES)
        ],
        "mcf": c.MCF,
        "permanents": [{"name": p[0], "img": c.P + p[1] + ".png", "role": p[2]} for p in c.PERMANENTS],
        "doctorants": [{"name": p[0], "aff": p[1], "img": c.P + p[2] + ".png"} for p in c.DOCTORANTS],
        "master_students": [{"name": p[0], "img": c.P + p[1] + ".png"} for p in c.MASTER_STUDENTS],
        "scientists": [
            {"name": s[0], "aff": s[1], "country": (s[2], c.COUNTRIES[s[2]]) if s[2] else None, "img": c.P + s[3] + ".png"}
            for s in c.SCIENTISTS
        ],
        "themes": [
            {"no": a[0], "title": a[1], "formula": a[2], "name": a[3], "img": "conference/img/themes/" + d[0] + ".webp",
             "cap": d[1], "kw": list(zip(d[2][0], d[2][1])),
             "credit": dict(zip(("author", "lic", "lic_url", "page", "note"), c.THEME_CREDITS[d[0]]))}
            for a, d in zip(c.AXES, c.THEME_DETAILS)
        ],
        "registered": [
            {"name": r[0], "aff": r[1], "country": (r[2], c.COUNTRIES[r[2]]) if r[2] else None,
             "ini": "".join(w[0] for w in r[0].split()[:2]).upper()}
            for r in c.REGISTERED
        ],
        "participants_total": len(c.SPEAKERS) + len(c.PERMANENTS) + len(c.DOCTORANTS) + len(c.REGISTERED),
        "perm_off": len(c.SPEAKERS),
        "doc_off": len(c.SPEAKERS) + len(c.PERMANENTS),
        "reg_off": len(c.SPEAKERS) + len(c.PERMANENTS) + len(c.DOCTORANTS),
        "participants_updated": c.PARTICIPANTS_UPDATED,
        "universities": [{"name": u[0], "img": c.P + u[1] + ".png"} for u in c.UNIVERSITIES],
        "si": c.SPECIAL_ISSUE,
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
