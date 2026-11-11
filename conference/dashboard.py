"""Tableau de bord d'administration : connexion, liste, ajout, modification, suppression, ajout en masse, export."""
import csv

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .forms import BulkForm, ParticipantForm, parse_bulk
from .models import Participant
from .participants import sort_key
from .roles import DEFAULT_ROLE, ROLES

MAX_FAILS, LOCK_SECONDS = 5, 15 * 60

staff_required = user_passes_test(lambda u: u.is_active and u.is_staff, login_url="/admin/connexion/")


def _guard(view):
    return never_cache(staff_required(view))


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return (forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "")) or "?"


def _lock_keys(request, username):
    return [f"login-fail:ip:{_client_ip(request)}", f"login-fail:user:{username.lower()[:80]}"]


@never_cache
def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dash_home")
    error, username = "", ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        keys = _lock_keys(request, username)
        if any(cache.get(k, 0) >= MAX_FAILS for k in keys):
            error = "Trop de tentatives. Réessayez dans quelques minutes."
        else:
            user = authenticate(request, username=username, password=request.POST.get("password", ""))
            if user is not None and user.is_staff:
                for k in keys:
                    cache.delete(k)
                login(request, user)
                nxt = request.POST.get("next", "")
                return redirect(nxt if nxt.startswith("/admin/") and not nxt.startswith("//") else "dash_home")
            for k in keys:
                cache.set(k, cache.get(k, 0) + 1, LOCK_SECONDS)
            error = "Identifiant ou mot de passe incorrect."
    return render(request, "dashboard/login.html", {"error": error, "username": username, "next": request.GET.get("next", "")})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("dash_login")


@_guard
def home(request):
    people = sorted(Participant.objects.all(), key=lambda p: (sort_key(p.name), p.pk))
    rows = [{"p": p, "country": p.country_fr, "role": p.role if p.role in ROLES else DEFAULT_ROLE,
             "role_label": ROLES[p.role if p.role in ROLES else DEFAULT_ROLE][0]} for p in people]
    last = max((p.updated_at for p in people), default=None)
    return render(request, "dashboard/home.html", {
        "rows": rows,
        "total": len(rows),
        "n_countries": len({c for p in people for c in p.codes}),
        "n_inst": len({p.institution.strip().lower() for p in people if p.institution.strip()}),
        "last": timezone.localtime(last) if last else None,
    })


@_guard
def add(request):
    form = ParticipantForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        p = form.save()
        messages.success(request, f"« {p.name} » a été ajouté à la liste.")
        if "again" in request.POST:
            return redirect("dash_add")
        return redirect("dash_home")
    return render(request, "dashboard/form.html", {"form": form, "title": "Ajouter un participant", "is_new": True})


@_guard
def edit(request, pk):
    p = get_object_or_404(Participant, pk=pk)
    form = ParticipantForm(request.POST or None, instance=p)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"« {p.name} » a été modifié.")
        return redirect("dash_home")
    return render(request, "dashboard/form.html", {"form": form, "title": "Modifier un participant", "p": p})


@_guard
def delete(request, pk):
    p = get_object_or_404(Participant, pk=pk)
    if request.method == "POST":
        name = p.name
        p.delete()
        messages.success(request, f"« {name} » a été supprimé de la liste.")
        return redirect("dash_home")
    return render(request, "dashboard/confirm_delete.html", {"p": p})


@_guard
def bulk(request):
    form = BulkForm(request.POST or None)
    errors = []
    if request.method == "POST" and form.is_valid():
        good, errors = parse_bulk(form.cleaned_data["lines"])
        if not errors and not good:
            errors = ["Aucune ligne à ajouter."]
        if not errors:
            existing = {(p.name.lower(), p.institution.lower()) for p in Participant.objects.all()}
            new, skipped = [], 0
            for name, inst, code, code2, role in good:
                key = (name.lower(), inst.lower())
                if key in existing:
                    skipped += 1
                    continue
                existing.add(key)
                new.append(Participant(name=name, institution=inst, country=code, country2=code2, role=role))
            now = timezone.now()
            for p in new:
                p.created_at = p.updated_at = now
            Participant.objects.bulk_create(new)
            msg = f"{len(new)} participant(s) ajouté(s)."
            if skipped:
                msg += f" {skipped} déjà présent(s), ignoré(s)."
            messages.success(request, msg)
            return redirect("dash_home")
    return render(request, "dashboard/bulk.html", {"form": form, "errors": errors})


@_guard
def export_csv(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="participants-m2isda-2027.csv"'
    response.write("﻿")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["Nom", "Établissement", "Établissement (anglais)", "Pays", "Statut"])
    for p in sorted(Participant.objects.all(), key=lambda p: (sort_key(p.name), p.pk)):
        writer.writerow([p.name, p.institution, p.institution_en, p.country_fr, p.role_fr])
    return response
