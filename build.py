#!/usr/bin/env python3
"""Static site generator for the portfolio. Python standard library only.

    python build.py                    build dist/ with the cached GitHub snapshot (data/github.json)
    python build.py --refresh-github   fetch fresh GitHub data first (uses $GITHUB_TOKEN if set)
    python build.py --release          strict: fail on drafts, missing translations or GitHub errors
    python build.py --serve            build, then serve dist/ on http://127.0.0.1:8000

Content lives in content/ (one JSON file per project), presentation in src/.
"""
from __future__ import annotations

import argparse
import datetime as dt
import functools
import hashlib
import html
import http.server
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
SRC = ROOT / "src"
DATA = ROOT / "data"
DIST = ROOT / "dist"

LANGS = ["es", "en", "gl"]
DEFAULT_LANG = "es"
HTML_LANG = {"es": "es", "en": "en", "gl": "gl"}
OG_LOCALE = {"es": "es_ES", "en": "en_GB", "gl": "gl_ES"}

UNIT = 20  # diagram grid unit, px
NODE_H = 3  # default node height, grid units
MONO_W = {13: 7.9, 11: 6.7, 10: 6.1}  # approx. JetBrains Mono advance per char at that font size

WARNINGS: list[str] = []


def warn(msg: str) -> None:
    if msg in WARNINGS:  # pages are rendered once per language; report each issue once
        return
    WARNINGS.append(msg)
    print(f"  ! {msg}", file=sys.stderr)


# --------------------------------------------------------------------------- content


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_content() -> dict:
    projects = [load_json(p) for p in sorted((CONTENT / "projects").glob("*.json"))]
    projects.sort(key=lambda p: (p.get("order", 999), p["id"]))
    return {
        "profile": load_json(CONTENT / "profile.json"),
        "ui": {lang: load_json(CONTENT / "i18n" / f"{lang}.json") for lang in LANGS},
        "projects": projects,
        "career": load_json(CONTENT / "career.json"),
        "skills": load_json(CONTENT / "skills.json"),
        "hero": load_json(CONTENT / "hero.json"),
    }


def key_paths(obj, prefix=""):
    """Yield every leaf path of a JSON value; lists count as leaves with their length."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from key_paths(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        yield f"{prefix}[{len(obj)}]"
    else:
        yield prefix


def validate(content: dict) -> list[str]:
    errors = []
    base = set(key_paths(content["ui"][DEFAULT_LANG]))
    for lang in LANGS:
        keys = set(key_paths(content["ui"][lang]))
        for k in sorted(base - keys):
            errors.append(f"i18n/{lang}.json is missing '{k}'")
        for k in sorted(keys - base):
            errors.append(f"i18n/{lang}.json has '{k}' that i18n/{DEFAULT_LANG}.json lacks")

    def check_localized(value, where):
        if isinstance(value, dict) and set(value) & set(LANGS):
            for lang in LANGS:
                if lang not in value:
                    errors.append(f"{where}: missing '{lang}' translation")
        elif isinstance(value, dict):
            for k, v in value.items():
                check_localized(v, f"{where}.{k}")
        elif isinstance(value, list):
            for i, v in enumerate(value):
                check_localized(v, f"{where}[{i}]")

    for p in content["projects"]:
        check_localized(p, f"projects/{p['id']}")
        for field in ("id", "title", "tagline", "summary"):
            if field not in p:
                errors.append(f"projects/{p['id']}: missing '{field}'")
    check_localized(content["career"], "career")
    check_localized(content["skills"], "skills")
    check_localized(content["hero"], "hero")
    return errors


def loc(value, lang: str):
    """Pick the translation of a {es,en,gl} value; plain values pass through."""
    if isinstance(value, dict) and DEFAULT_LANG in value:
        return value.get(lang, value[DEFAULT_LANG])
    return value


def fmt(template: str, **kw) -> str:
    return re.sub(r"\{(\w+)\}", lambda m: str(kw.get(m.group(1), m.group(0))), template)


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def md(text: str) -> str:
    """Escape, then allow **bold**, *em*, `code` and [links](https://… or #anchor)."""
    out = esc(text)
    out = re.sub(r"\[([^\]]+)\]\(((?:https://|#)[^)\s]+)\)", r'<a href="\2">\1</a>', out)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", out)
    return out


# --------------------------------------------------------------------------- github


API = "https://api.github.com"


def gh_request(url: str, token: str | None, data: bytes | None = None, accept="application/vnd.github+json"):
    req = urllib.request.Request(url, data=data, headers={
        "Accept": accept,
        "User-Agent": "portfolio-build",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = resp.read()
    return body if accept.startswith("text/") else json.loads(body)


def fetch_contributions(user: str, token: str | None) -> dict | None:
    if token:
        query = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
                   totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}"""
        res = gh_request(f"{API}/graphql", token,
                         json.dumps({"query": query, "variables": {"login": user}}).encode())
        cal = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        levels = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
        days = [{"date": d["date"], "count": d["contributionCount"], "level": levels[d["contributionLevel"]]}
                for w in cal["weeks"] for d in w["contributionDays"]]
        return {"total": cal["totalContributions"], "days": days}
    # Without a token, read the public calendar fragment GitHub renders on profile pages.
    page = gh_request(f"https://github.com/users/{user}/contributions", None, accept="text/html").decode()
    cells = re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*?id="([^"]+)"[^>]*?data-level="(\d)"', page)
    tips = dict(re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', page))
    days = []
    for date, cell_id, level in cells:
        m = re.match(r"(\d+)", tips.get(cell_id, ""))
        days.append({"date": date, "count": int(m.group(1)) if m else 0, "level": int(level)})
    if not days:
        return None
    days.sort(key=lambda d: d["date"])
    return {"total": sum(d["count"] for d in days), "days": days}


def fetch_github(user: str, token: str | None) -> dict:
    print(f"Fetching GitHub data for {user} ({'token' if token else 'anonymous'})...")
    prof = gh_request(f"{API}/users/{user}", token)
    repos = []
    page = 1
    while True:
        batch = gh_request(f"{API}/users/{user}/repos?per_page=100&type=owner&page={page}", token)
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    out_repos = []
    for r in repos:
        languages = {} if r["fork"] else gh_request(r["languages_url"], token)
        out_repos.append({
            "name": r["name"],
            "full_name": r["full_name"],
            "html_url": r["html_url"],
            "description": r["description"],
            "homepage": r["homepage"],
            "language": r["language"],
            "languages": languages,
            "stars": r["stargazers_count"],
            "forks": r["forks_count"],
            "fork": r["fork"],
            "archived": r["archived"],
            "license": (r.get("license") or {}).get("spdx_id"),
            "topics": r.get("topics", []),
            "created_at": r["created_at"],
            "pushed_at": r["pushed_at"],
        })
    try:
        contributions = fetch_contributions(user, token)
    except Exception as e:  # the calendar is decoration; never fail the build over it
        warn(f"contribution calendar unavailable: {e}")
        contributions = None
    return {
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "profile": {k: prof.get(k) for k in ("login", "name", "avatar_url", "html_url", "public_repos",
                                               "followers", "created_at")},
        "repos": out_repos,
        "contributions": contributions,
    }


def download_avatar(url: str) -> None:
    target = SRC / "img" / "avatar.jpg"
    try:
        req = urllib.request.Request(f"{url}&s=480" if "?" in url else f"{url}?s=480",
                                     headers={"User-Agent": "portfolio-build"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            target.write_bytes(resp.read())
    except Exception as e:
        warn(f"avatar download failed, keeping the existing one: {e}")


def load_github(refresh: bool, release: bool, user: str) -> dict:
    cache = DATA / "github.json"
    if refresh:
        try:
            data = fetch_github(user, os.environ.get("GITHUB_TOKEN"))
            DATA.mkdir(exist_ok=True)
            cache.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
            if data["profile"].get("avatar_url"):
                download_avatar(data["profile"]["avatar_url"])
            return data
        except (urllib.error.URLError, KeyError, TimeoutError) as e:
            if release and not cache.exists():
                raise SystemExit(f"GitHub fetch failed and there is no cache: {e}")
            warn(f"GitHub fetch failed, using cached snapshot: {e}")
    if cache.exists():
        return load_json(cache)
    warn("no GitHub data: run with --refresh-github")
    return {"fetched_at": None, "profile": {}, "repos": [], "contributions": None}


# --------------------------------------------------------------------------- diagrams

ICONS = {
    "user": '<circle cx="8" cy="5" r="3"/><path d="M2 15c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5"/>',
    "repo": '<circle cx="4" cy="3" r="1.6"/><circle cx="4" cy="13" r="1.6"/><circle cx="12" cy="5" r="1.6"/>'
            '<path d="M4 4.6v6.8M12 6.6c0 3.4-8 1.8-8 4.8"/>',
    "db": '<ellipse cx="8" cy="3.5" rx="5.5" ry="2"/><path d="M2.5 3.5v9c0 1.1 2.5 2 5.5 2s5.5-.9 5.5-2v-9'
          'M2.5 8c0 1.1 2.5 2 5.5 2s5.5-.9 5.5-2"/>',
    "external": '<path d="M4.5 13h7.6a3 3 0 0 0 .3-6 4.5 4.5 0 0 0-8.6-1.1A3.6 3.6 0 0 0 4.5 13z"/>',
    "service": '<path d="M8 1.5l6 3.5v6l-6 3.5-6-3.5V5z"/><path d="M8 8.5V15M8 8.5l6-3.5M8 8.5L2 5"/>',
    "controller": '<path d="M13.2 9.5A5.4 5.4 0 1 1 11.6 4"/><path d="M12.2 1.2v3.4H8.8"/>'
                  '<circle cx="8" cy="8.5" r="1.4"/>',
    "browser": '<rect x="1.5" y="2.5" width="13" height="11" rx="1.5"/><path d="M1.5 5.5h13"/>'
               '<path d="M4.5 9h4M4.5 11h6"/>',
    "lock": '<rect x="3" y="7" width="10" height="7.5" rx="1"/><path d="M5.5 7V5a2.5 2.5 0 0 1 5 0v2M8 10v1.8"/>',
    "doc": '<path d="M4 1.5h5.5l3 3v10H4z"/><path d="M9.5 1.5v3h3M6 8h4.5M6 10.5h4.5"/>',
    "cube": '<path d="M8 1.5l6 3.2v6.6L8 14.5l-6-3.2V4.7z"/><path d="M2 4.7l6 3.3 6-3.3M8 8v6.5"/>',
    "gateway": '<path d="M1.5 8h4.5M6 8l7-5M6 8h7M6 8l7 5"/><circle cx="13" cy="3" r="1.2"/>'
               '<circle cx="13" cy="8" r="1.2"/><circle cx="13" cy="13" r="1.2"/>',
}


def node_box(n: dict) -> tuple[float, float, float, float]:
    return n["x"] * UNIT, n["y"] * UNIT, n.get("w", 8) * UNIT, n.get("h", NODE_H) * UNIT


def route(a: dict, b: dict, edge: dict) -> list[tuple[float, float]]:
    """Orthogonal route between two node boxes, border to border."""
    ax, ay, aw, ah = node_box(a)
    bx, by, bw, bh = node_box(b)
    acx, acy, bcx, bcy = ax + aw / 2, ay + ah / 2, bx + bw / 2, by + bh / 2
    if ax + aw <= bx or bx + bw <= ax:  # side by side: horizontal - vertical - horizontal
        sx, ex = (ax + aw, bx) if bcx > acx else (ax, bx + bw)
        mx = edge["mid"] * UNIT if "mid" in edge else (sx + ex) / 2
        pts = [(sx, acy), (mx, acy), (mx, bcy), (ex, bcy)]
    else:  # stacked: vertical - horizontal - vertical
        sy, ey = (ay + ah, by) if bcy > acy else (ay, by + bh)
        my = edge["mid"] * UNIT if "mid" in edge else (sy + ey) / 2
        pts = [(acx, sy), (acx, my), (bcx, my), (bcx, ey)]
    dedup = [pts[0]]
    for p in pts[1:]:
        if abs(p[0] - dedup[-1][0]) > 0.01 or abs(p[1] - dedup[-1][1]) > 0.01:
            dedup.append(p)
    # drop collinear middle points so straight edges are a single segment
    clean = [dedup[0]]
    for i in range(1, len(dedup) - 1):
        (x0, y0), (x1, y1), (x2, y2) = clean[-1], dedup[i], dedup[i + 1]
        if not ((abs(x0 - x1) < .01 and abs(x1 - x2) < .01) or (abs(y0 - y1) < .01 and abs(y1 - y2) < .01)):
            clean.append(dedup[i])
    clean.append(dedup[-1])
    return clean


def rounded_path(pts: list[tuple[float, float]], r: float = 6) -> str:
    def n(v):
        return f"{v:.1f}".rstrip("0").rstrip(".")
    d = [f"M{n(pts[0][0])} {n(pts[0][1])}"]
    for i in range(1, len(pts) - 1):
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
        l1 = abs(x1 - x0) + abs(y1 - y0)
        l2 = abs(x2 - x1) + abs(y2 - y1)
        rr = min(r, l1 / 2, l2 / 2)
        ux, uy = ((x1 - x0) / l1, (y1 - y0) / l1) if l1 else (0, 0)
        vx, vy = ((x2 - x1) / l2, (y2 - y1) / l2) if l2 else (0, 0)
        d.append(f"L{n(x1 - ux * rr)} {n(y1 - uy * rr)}Q{n(x1)} {n(y1)} {n(x1 + vx * rr)} {n(y1 + vy * rr)}")
    d.append(f"L{n(pts[-1][0])} {n(pts[-1][1])}")
    return "".join(d)


def polyline_midpoint(pts):
    segs = [(pts[i], pts[i + 1], abs(pts[i + 1][0] - pts[i][0]) + abs(pts[i + 1][1] - pts[i][1]))
            for i in range(len(pts) - 1)]
    half = sum(s[2] for s in segs) / 2
    for (x0, y0), (x1, y1), length in segs:
        if half <= length and length:
            t = half / length
            return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        half -= length
    return pts[-1]


def text_width(s: str, size: int) -> float:
    return len(s) * MONO_W[size]


def render_diagram(spec: dict, lang: str, uid: str, title: str, extra_class: str = "") -> str:
    W, H = spec["cols"] * UNIT, spec["rows"] * UNIT
    nodes = {n["id"]: n for n in spec["nodes"]}
    o = [f'<svg class="dg {extra_class}" viewBox="-2 -2 {W + 4} {H + 4}" role="img" '
         f'aria-labelledby="{uid}-t" data-uid="{uid}">',
         f'<title id="{uid}-t">{esc(title)}</title>',
         f'<defs><marker id="{uid}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
         f'orient="auto-start-reverse"><path class="dg-arrow" d="M1 1.5L9 5L1 8.5"/></marker></defs>']

    for i, g in enumerate(spec.get("groups", [])):
        x, y, w, h = g["x"] * UNIT, g["y"] * UNIT, g["w"] * UNIT, g["h"] * UNIT
        label = loc(g.get("label", ""), lang)
        lw = text_width(label, 10) + 12
        t = 7  # corner bracket length
        brackets = "".join([
            f"M{x} {y + t}V{y}H{x + t}", f"M{x + w - t} {y}H{x + w}V{y + t}",
            f"M{x + w} {y + h - t}V{y + h}H{x + w - t}", f"M{x + t} {y + h}H{x}V{y + h - t}"])
        o.append(f'<g class="dg-group" data-i="{i}"><rect class="dg-group-box" x="{x}" y="{y}" width="{w}" height="{h}"/>'
                 f'<path class="dg-group-corner" d="{brackets}"/>'
                 f'<rect class="dg-group-tab" x="{x + 10}" y="{y - 7}" width="{lw:.0f}" height="14"/>'
                 f'<text class="dg-group-label" x="{x + 16}" y="{y + 3.5}">{esc(label)}</text></g>')

    for i, e in enumerate(spec["edges"]):
        a, b = nodes[e["from"]], nodes[e["to"]]
        pts = route(a, b, e)
        d = rounded_path(pts)
        o.append(f'<g class="dg-edge-g" data-from="{e["from"]}" data-to="{e["to"]}" data-i="{i}">'
                 f'<path class="dg-edge" d="{d}" pathLength="1" marker-end="url(#{uid}-arrow)"/>'
                 f'<path class="dg-flow" d="{d}"/>')
        if e.get("label"):
            label = loc(e["label"], lang)
            mx, my = polyline_midpoint(pts)
            lw = text_width(label, 10) + 10
            o.append(f'<g class="dg-elabel"><rect x="{mx - lw / 2:.1f}" y="{my - 8:.1f}" width="{lw:.1f}" '
                     f'height="16" rx="2"/><text x="{mx:.1f}" y="{my + 3.5:.1f}">{esc(label)}</text></g>')
        o.append("</g>")

    for i, n in enumerate(spec["nodes"]):
        x, y, w, h = node_box(n)
        kind = n.get("kind", "service")
        label, sub = loc(n["label"], lang), loc(n.get("sub", ""), lang)
        if max(text_width(label, 13), text_width(sub, 11)) + 44 > w:
            warn(f"diagram {uid}: label of node '{n['id']}' may overflow ({label!r} in {w:.0f}px)")
        cls = f"dg-node kind-{kind}" + (" accent" if n.get("accent") else "") + (" is-link" if n.get("href") else "")
        ty = h / 2 + (-2 if sub else 4)
        inner = [f'<rect class="dg-box" width="{w}" height="{h}" rx="3"/>']
        if kind == "gateway":
            inner.append(f'<rect class="dg-box-inner" x="3" y="3" width="{w - 6}" height="{h - 6}" rx="2"/>')
        inner.append(f'<g class="dg-icon" transform="translate(12 {h / 2 - 8:.1f})">{ICONS.get(kind, ICONS["service"])}</g>')
        inner.append(f'<text class="dg-label" x="36" y="{ty:.1f}">{esc(label)}</text>')
        if sub:
            inner.append(f'<text class="dg-sub" x="36" y="{ty + 14:.1f}">{esc(sub)}</text>')
        body = "".join(inner)
        g = (f'<g class="{cls}" data-id="{n["id"]}" data-i="{i}" transform="translate({x:.0f} {y:.0f})">'
             f'{body}</g>')
        if n.get("href"):
            g = f'<a class="dg-link" href="{esc(n["href"])}" aria-label="{esc(sub or label)}">{g}</a>'
        o.append(g)
    o.append("</svg>")
    return "".join(o)


# --------------------------------------------------------------------------- page helpers


def section_head(sid: str, no: int, ui: dict, title: str, intro: str | None = None) -> str:
    label = ui["nav"][sid]
    return (f'<header class="sheet-head reveal">'
            f'<p class="sheet-label"><span class="sheet-no">{no:02d}</span><span>{esc(label)}</span></p>'
            f'<h2 id="{sid}-h">{md(title)}</h2>'
            + (f'<p class="sheet-intro">{md(intro)}</p>' if intro else "")
            + f'<span class="sheet-ref" aria-hidden="true">TF-DWG-{no:02d} · REV {dt.date.today():%y.%m}</span>'
            f'</header>')


def fmt_date(iso: str | None, ui: dict, with_day=False) -> str:
    if not iso:
        return ""
    d = dt.date.fromisoformat(iso[:10])
    m = ui["months"][d.month - 1]
    return f"{d.day} {m} {d.year}" if with_day else f"{m} {d.year}"


def years_since(year: int) -> int:
    return dt.date.today().year - year


ICON_SVG = {
    "github": '<path d="M12 .5a11.5 11.5 0 0 0-3.6 22.4c.6.1.8-.3.8-.6v-2c-3.2.7-3.9-1.5-3.9-1.5-.5-1.3-1.3-1.7-1.3-1.7'
              '-1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.7-1.6-2.6-.3-5.3-1.3-5.3-5.7 '
              '0-1.3.5-2.3 1.2-3.1-.1-.3-.5-1.5.1-3.1 0 0 1-.3 3.2 1.2a11 11 0 0 1 5.8 0C17.3 4.7 18.3 5 18.3 5c.6 '
              '1.6.2 2.8.1 3.1.8.8 1.2 1.9 1.2 3.1 0 4.4-2.7 5.4-5.3 5.7.4.4.8 1.1.8 2.2v3.2c0 .3.2.7.8.6A11.5 11.5 '
              '0 0 0 12 .5z" fill="currentColor" stroke="none"/>',
    "linkedin": '<path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3zM9.5 9.5h3.8v1.6h.1c.5-1 '
                '1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.2c0-1.2 0-2.8-1.7-2.8s-2 1.3-2 2.7V21h-4z" '
                'fill="currentColor" stroke="none"/>',
    "mail": '<rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="M3 6.5l9 6.5 9-6.5"/>',
    "star": '<path d="M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8-4.3-4.1 5.9-.8z"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "flag": '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
    "scale": '<path d="M12 3v18M5 7h14M5 7l-3 7a3.5 3.5 0 0 0 6 0zM19 7l-3 7a3.5 3.5 0 0 0 6 0z"/>',
    "ext": '<path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
    "code": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M13.5 4l-3 16"/>',
    "download": '<path d="M12 4v11M7 10.5l5 5 5-5M4.5 20h15"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8'
           'M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/>',
    "moon": '<path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5z"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "arrow-up": '<path d="M12 19V5M6 11l6-6 6 6"/>',
}


def icon(name: str, cls: str = "ic") -> str:
    return (f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
            f'{ICON_SVG[name]}</svg>')


# --------------------------------------------------------------------------- sections


def render_nav(c: dict, lang: str, ui: dict, base: str) -> str:
    ids = ["about", "projects", "career", "stack", "github", "contact"]
    links = "".join(f'<li><a href="#{i}" data-nav="{i}">{esc(ui["nav"][i])}</a></li>' for i in ids)
    current = ' aria-current="page"'
    langs = "".join(
        f'<li><a href="{base}{"" if l == DEFAULT_LANG else l + "/"}" hreflang="{l}" lang="{l}" '
        f'class="lang-link{" is-current" if l == lang else ""}"'
        f'{current if l == lang else ""} title="{esc(c["ui"][l]["langName"])}">{l.upper()}</a></li>'
        for l in LANGS)
    home = base if lang == DEFAULT_LANG else f"{base}{lang}/"
    return f"""
<header class="topbar" id="topbar">
  <a class="brand" href="{home}#top" aria-label="{esc(c['profile']['name'])}">
    <span class="brand-mark" aria-hidden="true">{esc(c['profile']['initials'])}</span>
    <span class="brand-name">{esc(c['profile']['shortName'])}</span>
  </a>
  <nav class="nav" aria-label="{esc(ui['nav']['menu'])}">
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav-links">
      {icon('menu')}<span class="visually-hidden">{esc(ui['nav']['menu'])}</span>
    </button>
    <ul class="nav-links" id="nav-links">{links}</ul>
  </nav>
  <div class="tools">
    <ul class="langs" aria-label="{esc(ui['nav']['language'])}">{langs}</ul>
    <button class="theme-toggle" type="button" aria-label="{esc(ui['nav']['theme'])}" title="{esc(ui['nav']['theme'])}">
      {icon('sun', 'ic ic-sun')}{icon('moon', 'ic ic-moon')}
    </button>
  </div>
</header>"""


def render_hero(c: dict, lang: str, ui: dict) -> str:
    p = c["profile"]
    h = ui["hero"]
    t = ui["titleblock"]
    years = years_since(p["careerStart"])
    diagram = render_diagram(c["hero"], lang, "hero", h["diagramLabel"], "dg-hero")
    first, _, rest = p["name"].partition(" ")
    return f"""
<section class="hero" id="top" aria-labelledby="hero-name">
  <div class="hero-text">
    <p class="kicker"><span class="kicker-dot" aria-hidden="true"></span>{esc(h['kicker'])}</p>
    <h1 id="hero-name"><span class="greet">{esc(h['greeting'])}</span>
      <span class="name"><span class="name-line">{esc(first)}</span> <span class="name-line">{esc(rest)}</span></span>
    </h1>
    <div class="dim-line" aria-hidden="true"><span>{years} {esc(ui['about']['figYears'].split(' ')[0])}</span></div>
    <p class="lead">{md(fmt(h['lead'], years=years))}</p>
  </div>
  <figure class="hero-diagram">
    {diagram}
    <figcaption>{esc(h['diagramHint'])}</figcaption>
  </figure>
  <dl class="titleblock" aria-hidden="true">
    <div><dt>{esc(t['project'])}</dt><dd>{esc(t['projectValue'])}</dd></div>
    <div><dt>{esc(t['author'])}</dt><dd>{esc(p['name'])}</dd></div>
    <div><dt>{esc(t['scale'])}</dt><dd>1:1</dd></div>
    <div><dt>{esc(t['rev'])}</dt><dd>{dt.date.today():%Y.%m}</dd></div>
    <div><dt>{esc(t['sheet'])}</dt><dd>01 / 06</dd></div>
  </dl>
  <a class="scroll-cue" href="#about" aria-label="{esc(h['scroll'])}"><span aria-hidden="true"></span></a>
</section>"""


def render_about(c: dict, lang: str, ui: dict, gh: dict, base: str) -> str:
    a = ui["about"]
    p = c["profile"]
    own = [r for r in gh.get("repos", []) if not r["fork"]]
    stars = sum(r["stars"] for r in own)
    repos = gh.get("profile", {}).get("public_repos") or len(gh.get("repos", []))
    since = (gh.get("profile", {}).get("created_at") or "")[:4]
    figs = [(years_since(p["careerStart"]), a["figYears"]), (repos, a["figRepos"]), (stars, a["figStars"])]
    if since:
        figs.append((since, a["figSince"]))
    fig_html = "".join(f'<div class="fig"><dt>{esc(label)}</dt><dd data-count="{esc(v)}">{esc(v)}</dd></div>'
                       for v, label in figs)
    body = "".join(f"<p>{md(fmt(par, careerStart=p['careerStart']))}</p>" for par in a["body"])
    return f"""
<section class="sheet" id="about" aria-labelledby="about-h">
  {section_head('about', 2, ui, a['title'])}
  <div class="about-grid">
    <figure class="portrait reveal">
      <div class="portrait-frame">
        <img src="{base}assets/img/avatar.jpg" width="320" height="320" alt="{esc(fmt(a['portrait'], name=p['name']))}" loading="lazy" decoding="async">
        <span class="crosshair tl"></span><span class="crosshair tr"></span><span class="crosshair bl"></span><span class="crosshair br"></span>
      </div>
      <figcaption><span>FIG. 1</span><span>{esc(c['profile']['location'][lang])}</span></figcaption>
    </figure>
    <div class="about-body reveal">
      {body}
      <dl class="figures">{fig_html}</dl>
    </div>
  </div>
</section>"""


def repo_index(gh: dict) -> dict:
    return {r["full_name"].lower(): r for r in gh.get("repos", [])}


def render_projects(c: dict, lang: str, ui: dict, gh: dict) -> str:
    pu = ui["projects"]
    idx = repo_index(gh)
    featured = [p for p in c["projects"] if p.get("featured")]
    others = [p for p in c["projects"] if not p.get("featured")]
    arts = []
    for n, p in enumerate(featured, 1):
        title = loc(p["title"], lang)
        r = idx.get(p.get("repo", "").lower(), {})
        site_repos = [idx[s["repo"].lower()] for s in p.get("sites", []) if s.get("repo", "").lower() in idx]
        meta = []
        if r:
            meta.append(f'<li>{icon("star")}<span><strong>{r["stars"]}</strong> {esc(pu["stars"])}</span></li>')
            meta.append(f'<li>{icon("clock")}<span>{esc(pu["updated"])} {esc(fmt_date(r["pushed_at"], ui))}</span></li>')
            meta.append(f'<li>{icon("flag")}<span>{esc(pu["since"])} {r["created_at"][:4]}</span></li>')
            if r.get("license") and r["license"] != "NOASSERTION":
                meta.append(f'<li>{icon("scale")}<span>{esc(r["license"])}</span></li>')
        elif site_repos:  # a group of sites: aggregate what GitHub knows about them
            stars = sum(sr["stars"] for sr in site_repos)
            pushed = max(sr["pushed_at"] for sr in site_repos)
            since = min(sr["created_at"] for sr in site_repos)[:4]
            meta.append(f'<li>{icon("star")}<span><strong>{stars}</strong> {esc(pu["stars"])}</span></li>')
            meta.append(f'<li>{icon("clock")}<span>{esc(pu["updated"])} {esc(fmt_date(pushed, ui))}</span></li>')
            meta.append(f'<li>{icon("flag")}<span>{esc(pu["since"])} {since}</span></li>')
        sites = ""
        if p.get("sites"):
            rows = []
            for s in p["sites"]:
                sr = idx.get(s.get("repo", "").lower())
                code = (f'<a class="site-code" href="https://github.com/{esc(s["repo"])}">{icon("code")}'
                        f'{esc(pu["repo"])}</a>') if s.get("repo") else ""
                star = f'<span class="site-stars">{icon("star")}{sr["stars"]}</span>' if sr else ""
                rows.append(f'<li><a class="site-title" href="{esc(loc(s["url"], lang))}">{esc(loc(s["title"], lang))}{icon("ext")}</a>'
                            f'<p>{md(loc(s["desc"], lang))}</p>'
                            f'<p class="site-meta"><span>{esc(loc(s.get("stack", ""), lang))}</span>{star}{code}</p></li>')
            sites = f'<ul class="sites">{"".join(rows)}</ul>'
        highlights = "".join(f"<li>{md(h)}</li>" for h in loc(p.get("highlights", []), lang))
        chips = "".join(f'<li>{esc(s)}</li>' for s in p.get("stack", []))
        related = ""
        if p.get("related"):
            rl = ", ".join(f'<a href="https://github.com/{esc(rr)}">{esc(rr.split("/")[-1])}</a>' for rr in p["related"])
            related = f'<p class="related"><span>{esc(pu["related"])}:</span> {rl}</p>'
        links = p.get("links", {})
        actions = []
        if p.get("repo"):
            actions.append(f'<a class="btn btn-sm" href="https://github.com/{esc(p["repo"])}">{icon("code")}{esc(pu["repo"])}</a>')
        if links.get("demo"):
            label = loc(links["demoLabel"], lang) if links.get("demoLabel") else pu["demo"]
            actions.append(f'<a class="btn btn-sm btn-primary" href="{esc(loc(links["demo"], lang))}">{icon("ext")}{esc(label)}</a>')
        if links.get("download"):
            actions.append(f'<a class="btn btn-sm btn-primary" href="{esc(links["download"])}">{icon("download")}{esc(pu["download"])}</a>')
        for extra in links.get("more", []):   # other places to find it (a store, a second site…)
            actions.append(f'<a class="btn btn-sm" href="{esc(loc(extra["url"], lang))}">{icon("ext")}{esc(loc(extra["label"], lang))}</a>')
        diagram = ""
        if p.get("diagram"):
            diagram = (f'<figure class="project-diagram">'
                       f'{render_diagram(p["diagram"], lang, "p-" + p["id"], fmt(pu["diagram"], name=title))}'
                       f'<figcaption>FIG. P-{n:02d} · {esc(title)}</figcaption></figure>')
        lang_bar = render_repo_languages(r.get("languages", {})) if r else ""
        arts.append(f"""
  <article class="project reveal{' flip' if n % 2 == 0 else ''}" id="project-{esc(p['id'])}" aria-labelledby="project-{esc(p['id'])}-h">
    <div class="project-text">
      <p class="project-no">P-{n:02d}</p>
      <h3 id="project-{esc(p['id'])}-h">{esc(title)}</h3>
      <p class="tagline">{md(loc(p['tagline'], lang))}</p>
      <ul class="meta">{''.join(meta)}</ul>
      <p class="summary">{md(loc(p['summary'], lang))}</p>
      {sites}
      {f'<h4>{esc(pu["highlights"])}</h4><ul class="highlights">{highlights}</ul>' if highlights else ''}
      <ul class="chips" aria-label="Stack">{chips}</ul>
      {lang_bar}
      {related}
      <div class="actions">{''.join(actions)}</div>
    </div>
    {diagram}
  </article>""")
    other_html = ""
    if others:
        cards = "".join(render_card(loc(p["title"], lang), loc(p["tagline"], lang), p.get("repo"), loc(p.get("links", {}).get("demo"), lang),
                                    idx.get(p.get("repo", "").lower()), ui) for p in others)
        other_html = f'<h3 class="sub-title reveal">{esc(pu["otherTitle"])}</h3><div class="cards">{cards}</div>'
    return f"""
<section class="sheet" id="projects" aria-labelledby="projects-h">
  {section_head('projects', 3, ui, pu['title'], pu['intro'])}
  <div class="projects">{''.join(arts)}</div>
  {other_html}
</section>"""


def render_repo_languages(langs: dict) -> str:
    total = sum(langs.values())
    if not total:
        return ""
    parts = sorted(langs.items(), key=lambda kv: -kv[1])
    items = "".join(f'<li><span class="lang-dot {lang_class(k)}"></span>{esc(k)} '
                    f'<span class="pct">{v * 100 / total:.0f}%</span></li>'
                    for k, v in parts if v * 100 / total >= 1)
    return f'<ul class="repo-langs">{items}</ul>'


def render_card(title, desc, repo, demo, r, ui) -> str:
    stars = f'<span>{icon("star")}{r["stars"]}</span>' if r else ""
    lang = f'<span><span class="lang-dot {lang_class(r["language"])}"></span>{esc(r["language"])}</span>' \
        if r and r.get("language") else ""
    updated = f'<span>{icon("clock")}{esc(fmt_date(r["pushed_at"], ui))}</span>' if r else ""
    href = demo or (f"https://github.com/{repo}" if repo else "#")
    return (f'<a class="card reveal" href="{esc(href)}">'
            f'<h4>{esc(title)}</h4><p>{esc(desc or ui["github"]["noDescription"])}</p>'
            f'<p class="card-meta">{lang}{stars}{updated}</p></a>')


def render_career(c: dict, lang: str, ui: dict, release: bool) -> str:
    cu = ui["career"]
    tracks = {"work": cu["trackWork"], "oss": cu["trackOss"], "edu": cu["trackEdu"]}
    items = []
    for i, e in enumerate(c["career"]["entries"]):
        if e.get("draft"):
            msg = f"career entry #{i + 1} ({loc(e['role'], DEFAULT_LANG)}) is still a draft"
            if release:
                raise SystemExit(f"error: {msg}; complete it or remove it from content/career.json")
            warn(msg)
        start, end = e.get("start"), e.get("end")
        when = f"{start or '····'}"
        if e.get("current"):
            when += f" — {cu['present']}"
        elif end and end != start:
            when += f" — {end}"
        tags = "".join(f"<li>{esc(loc(t, lang))}</li>" for t in e.get("tags", []))
        org = loc(e.get("org"), lang)
        summary = loc(e.get("summary"), lang)
        points = "".join(f"<li>{md(p)}</li>" for p in loc(e.get("points", []), lang))
        link = e.get("link")
        role = esc(loc(e["role"], lang))
        if link:
            role = f'<a href="{esc(link)}">{role}</a>'
        # Zigzag layout by class, not :nth-child, so the JS filter can re-flow the visible entries.
        side = (" is-right" if i % 2 else "") + (" is-after" if i else "")
        items.append(f"""
    <li class="tl-item track-{e['track']}{side}{' is-draft' if e.get('draft') else ''}{' is-current' if e.get('current') else ''} reveal" data-track="{e['track']}">
      <span class="tl-node" aria-hidden="true"></span>
      <div class="tl-card">
        <p class="tl-meta"><span class="tl-when">{esc(when)}</span><span class="tl-track">{esc(tracks[e['track']])}</span>
          {f'<span class="tl-draft">{esc(cu["draft"])}</span>' if e.get('draft') else ''}</p>
        <h3>{role}</h3>
        {f'<p class="tl-org">{esc(org)}</p>' if org else ''}
        {f'<p class="tl-summary">{md(summary)}</p>' if summary else ''}
        {f'<ul class="tl-points">{points}</ul>' if points else ''}
        {f'<ul class="chips chips-sm">{tags}</ul>' if tags else ''}
      </div>
    </li>""")
    # The legend doubles as a filter: with JS each entry is a toggle button; without JS it is just a legend.
    buttons = [f'<li><button type="button" class="tl-all" data-filter="all" aria-pressed="true">{esc(cu["filterAll"])}</button></li>']
    buttons += [f'<li class="track-{k}"><button type="button" data-filter="{k}" aria-pressed="false">'
                f'<span aria-hidden="true"></span>{esc(v)}</button></li>' for k, v in tracks.items()]
    return f"""
<section class="sheet" id="career" aria-labelledby="career-h">
  {section_head('career', 4, ui, cu['title'], cu['intro'])}
  <ul class="tl-legend reveal" role="group" aria-label="{esc(cu['filter'])}">{''.join(buttons)}</ul>
  <ol class="timeline">{''.join(items)}</ol>
</section>"""


def render_stack(c: dict, lang: str, ui: dict) -> str:
    su = ui["stack"]
    s = c["skills"]
    cross = s["crosscut"]
    cross_items = "".join(f"<li>{esc(loc(i, lang))}</li>" for i in cross["items"])
    layers = []
    for n, layer in enumerate(s["layers"], 1):
        chips = "".join(f"<li>{esc(loc(i, lang))}</li>" for i in layer["items"])
        layers.append(f'<li class="layer reveal" data-layer="{esc(layer["id"])}">'
                      f'<p class="layer-name"><span class="layer-no">L{n}</span>{esc(loc(layer["label"], lang))}</p>'
                      f'<ul class="chips">{chips}</ul></li>')
    return f"""
<section class="sheet" id="stack" aria-labelledby="stack-h">
  {section_head('stack', 5, ui, su['title'], su['intro'])}
  <div class="layers">
    <div class="crosscut reveal">
      <p class="crosscut-label"><span>{esc(loc(cross['label'], lang))}</span><small>{esc(su['crosscut'])}</small></p>
      <ul>{cross_items}</ul>
    </div>
    <ol class="layer-list">{''.join(layers)}</ol>
  </div>
</section>"""


LANG_SLOTS = 8  # categorical palette size; more languages fold into "other"
LANG_CLASS: dict[str, str] = {}  # language -> palette slot, fixed by overall rank (see language_totals)


def language_totals(gh: dict, exclude: set) -> list[tuple[str, int]]:
    totals: dict[str, int] = {}
    for r in gh.get("repos", []):
        if r["fork"] or r["name"] in exclude:
            continue
        for k, v in r.get("languages", {}).items():
            totals[k] = totals.get(k, 0) + v
    return sorted(totals.items(), key=lambda kv: -kv[1])


def assign_language_slots(gh: dict, exclude: set) -> None:
    ranked = language_totals(gh, exclude)
    named = ranked[:LANG_SLOTS - 1] if len(ranked) > LANG_SLOTS else ranked
    LANG_CLASS.clear()
    LANG_CLASS.update({k: f"s{i + 1}" for i, (k, _) in enumerate(named)})


def lang_class(name: str | None) -> str:
    return LANG_CLASS.get(name or "", "s-other")


def render_heatmap(contrib: dict, ui: dict) -> str:
    days = contrib["days"][-371:]
    if not days:
        return ""
    first = dt.date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # weeks start on Sunday, like GitHub
    cell, gap = 11, 3
    cols = (len(days) + offset + 6) // 7
    W, H = cols * (cell + gap), 7 * (cell + gap) + 18
    rects, months, last_month = [], [], None
    for i, d in enumerate(days):
        k = i + offset
        col, row = divmod(k, 7)
        x, y = col * (cell + gap), row * (cell + gap) + 18
        date = dt.date.fromisoformat(d["date"])
        tip = fmt(ui["github"]["contribDay"], count=d["count"], date=fmt_date(d["date"], ui, with_day=True))
        rects.append(f'<rect class="hm l{d["level"]}" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
                     f'data-tip="{esc(tip)}"/>')
        if date.day <= 7 and date.month != last_month and col < cols - 2:
            months.append(f'<text class="hm-month" x="{col * (cell + gap)}" y="10">{esc(ui["months"][date.month - 1])}</text>')
            last_month = date.month
    legend = "".join(f'<span class="hm-sw l{i}"></span>' for i in range(5))
    total = fmt(ui["github"]["contributions"], count=f"{contrib['total']:,}".replace(",", "."))
    return f"""
    <figure class="heatmap reveal">
      <figcaption><strong>{esc(total)}</strong></figcaption>
      <div class="heatmap-scroll"><svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(ui['github']['contribLabel'])}">{''.join(months)}{''.join(rects)}</svg></div>
      <p class="hm-legend"><span>{esc(ui['github']['less'])}</span>{legend}<span>{esc(ui['github']['more'])}</span></p>
    </figure>"""


def render_languages(gh: dict, ui: dict, exclude: set) -> str:
    ranked = language_totals(gh, exclude)
    total = sum(v for _, v in ranked)
    if not total:
        return ""
    shown = [(k, v) for k, v in ranked if k in LANG_CLASS]
    rest = total - sum(v for _, v in shown)
    series = [(k, v, LANG_CLASS[k]) for k, v in shown]
    if rest:
        series.append((ui["github"]["other"], rest, "s-other"))
    W, H, gap = 1000, 14, 2
    x, segs = 0.0, []
    usable = W - gap * (len(series) - 1)
    for i, (name, v, cls) in enumerate(series):
        w = max(usable * v / total, 2)
        pct = v * 100 / total
        segs.append(f'<rect class="lang-seg {cls}" x="{x:.1f}" y="0" width="{w:.1f}" height="{H}" '
                    f'data-tip="{esc(name)} · {pct:.1f}%"/>')
        x += w + gap
    legend = "".join(f'<li><span class="sw {cls}" aria-hidden="true"></span>{esc(name)}'
                     f'<span class="pct">{v * 100 / total:.1f}%</span></li>' for name, v, cls in series)
    return f"""
    <figure class="langbar reveal">
      <figcaption>{esc(ui['github']['languages'])}</figcaption>
      <svg viewBox="0 0 {W} {H}" preserveAspectRatio="none" role="img" aria-label="{esc(ui['github']['languages'])}">
        <clipPath id="langclip"><rect width="{W}" height="{H}" rx="4"/></clipPath>
        <g clip-path="url(#langclip)">{''.join(segs)}</g>
      </svg>
      <ul class="lang-legend">{legend}</ul>
    </figure>"""


def render_github(c: dict, lang: str, ui: dict, gh: dict) -> str:
    g = ui["github"]
    p = c["profile"]
    exclude = set(p["github"]["exclude"])
    heat = render_heatmap(gh["contributions"], ui) if gh.get("contributions") else ""
    fetched = (f'<p class="fetched">{esc(fmt(g["fetched"], date=fmt_date(gh["fetched_at"], ui, with_day=True)))}</p>'
               if gh.get("fetched_at") else "")
    return f"""
<section class="sheet" id="github" aria-labelledby="github-h">
  {section_head('github', 6, ui, g['title'])}
  <div class="gh-viz">
    {heat}
    {render_languages(gh, ui, exclude)}
  </div>
  <p class="all-repos reveal"><a class="btn" href="{esc(p['links']['github'])}?tab=repositories">{icon('github')}{esc(g['all'])}</a></p>
  {fetched}
</section>"""


def render_footer(c: dict, ui: dict) -> str:
    """Footer with the contact block (the nav and the hero diagram link to #contact)."""
    f = ui["footer"]
    cu = ui["contact"]
    p = c["profile"]
    return f"""
<footer class="footer" id="contact" aria-labelledby="contact-h">
  <div class="footer-contact">
    <div class="footer-cta">
      <h2 id="contact-h">{esc(cu['title'])}</h2>
      <p>{esc(cu['body'])}</p>
    </div>
    <ul class="contact-list">
      <li><a class="contact-item js-mail" href="{esc(p['links']['linkedin'])}" data-u="{esc(p['email']['user'])}" data-d="{esc(p['email']['domain'])}">
        {icon('mail')}<span><small>{esc(cu['email'])}</small><span class="js-mail-text">{esc(p['email']['user'])} [at] {esc(p['email']['domain'])}</span></span></a></li>
      <li><a class="contact-item" href="{esc(p['links']['linkedin'])}">{icon('linkedin')}<span><small>{esc(cu['linkedin'])}</small>antonio-ferreiro-couto</span></a></li>
      <li><a class="contact-item" href="{esc(p['links']['github'])}">{icon('github')}<span><small>{esc(cu['github'])}</small>@{esc(p['github']['user'])}</span></a></li>
    </ul>
  </div>
  <div class="footer-base">
    <p>© {dt.date.today().year} {esc(p['name'])}. {esc(f['built'])}</p>
    <p class="footer-links"><a href="https://github.com/{esc(p['sourceRepo'])}">{icon('code')}{esc(f['source'])}</a>
      <a href="#top">{icon('arrow-up')}{esc(f['top'])}</a></p>
  </div>
</footer>"""


# --------------------------------------------------------------------------- assembly


def asset_url(base: str, rel: str) -> str:
    digest = hashlib.sha256((SRC / rel).read_bytes()).hexdigest()[:10]
    return f"{base}assets/{rel}?v={digest}"


def page_url(site: str, lang: str) -> str:
    return site if lang == DEFAULT_LANG else f"{site}{lang}/"


def render_page(c: dict, lang: str, gh: dict, base: str, release: bool) -> str:
    ui = c["ui"][lang]
    p = c["profile"]
    site = p["siteUrl"]
    alternates = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{page_url(site, l)}">' for l in LANGS)
    alternates += f'\n<link rel="alternate" hreflang="x-default" href="{site}">'
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": p["name"],
        "alternateName": p["shortName"],
        "jobTitle": ui["hero"]["kicker"].split("·")[0].strip(),
        "url": page_url(site, lang),
        "image": f"{site}assets/img/avatar.jpg",
        "address": {"@type": "PostalAddress", "addressRegion": "Galicia", "addressCountry": "ES"},
        "alumniOf": "Universidade de Vigo",
        "worksFor": {"@type": "Organization", "name": p["worksFor"]},
        "sameAs": [p["links"]["github"], p["links"]["linkedin"]],
    }
    js_strings = {"lang": lang}
    body = "".join([
        f'<a class="skip" href="#main">{esc(ui["nav"]["skip"])}</a>',
        '<div class="bg-grid" aria-hidden="true"></div>',
        render_nav(c, lang, ui, base),
        '<main id="main">',
        render_hero(c, lang, ui),
        render_about(c, lang, ui, gh, base),
        render_projects(c, lang, ui, gh),
        render_career(c, lang, ui, release),
        render_stack(c, lang, ui),
        render_github(c, lang, ui, gh),
        "</main>",
        render_footer(c, ui),
        '<div class="readout" aria-hidden="true"><span class="rx">X 0000</span><span class="ry">Y 0000</span></div>',
        '<div class="tip" role="tooltip" hidden></div>',
    ])
    template = (SRC / "template.html").read_text(encoding="utf-8")
    values = {
        "lang": HTML_LANG[lang],
        "title": esc(ui["meta"]["title"]),
        "description": esc(ui["meta"]["description"]),
        "canonical": page_url(site, lang),
        "alternates": alternates,
        "og_locale": OG_LOCALE[lang],
        "og_image": f"{site}assets/img/avatar.jpg",
        "site_name": esc(p["name"]),
        "base": base,
        "css": asset_url(base, "css/main.css"),
        "theme_js": asset_url(base, "js/theme.js"),
        "main_js": asset_url(base, "js/main.js"),
        "font_preload": f"{base}assets/fonts/space-grotesk.woff2",
        "jsonld": json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/"),
        "js_strings": esc(json.dumps(js_strings, ensure_ascii=False)),
        "body": body,
    }

    def sub(m):
        key = m.group(1)
        if key not in values:
            raise SystemExit(f"template placeholder '{{{{{key}}}}}' has no value")
        return values[key]
    return re.sub(r"\{\{\s*(\w+)\s*\}\}", sub, template)


def build(args) -> None:
    content = load_content()
    errors = validate(content)
    if errors:
        for e in errors:
            print(f"  x {e}", file=sys.stderr)
        raise SystemExit(f"{len(errors)} content error(s)")
    gh = load_github(args.refresh_github, args.release, content["profile"]["github"]["user"])
    assign_language_slots(gh, set(content["profile"]["github"]["exclude"]))

    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    for sub in ("css", "js", "fonts", "img"):
        if (SRC / sub).exists():
            shutil.copytree(SRC / sub, DIST / "assets" / sub)
    shutil.copy(SRC / "favicon.svg", DIST / "assets" / "favicon.svg")
    shutil.copy(SRC / "favicon.svg", DIST / "favicon.svg")

    for lang in LANGS:
        out = DIST if lang == DEFAULT_LANG else DIST / lang
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(render_page(content, lang, gh, args.base, args.release), encoding="utf-8", newline="\n")
        print(f"  ✓ {out.relative_to(ROOT).as_posix()}/index.html")

    site = content["profile"]["siteUrl"]
    today = dt.date.today().isoformat()
    urls = "".join(
        f"<url><loc>{page_url(site, l)}</loc><lastmod>{today}</lastmod>"
        + "".join(f'<xhtml:link rel="alternate" hreflang="{a}" href="{page_url(site, a)}"/>' for a in LANGS)
        + "</url>" for l in LANGS)
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        f'xmlns:xhtml="http://www.w3.org/1999/xhtml">{urls}</urlset>\n', encoding="utf-8", newline="\n")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {site}sitemap.xml\n", encoding="utf-8", newline="\n")
    (DIST / ".nojekyll").write_text("", encoding="utf-8", newline="\n")
    shutil.copy(DIST / "index.html", DIST / "404.html")
    print(f"Built {len(LANGS)} languages into dist/ ({len(WARNINGS)} warning(s)).")


def serve(port: int) -> None:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"Serving dist/ on http://127.0.0.1:{port}/  (Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


def main() -> None:
    for stream in (sys.stdout, sys.stderr):  # Windows consoles default to a legacy code page
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refresh-github", action="store_true", help="fetch fresh data from the GitHub API")
    ap.add_argument("--release", action="store_true", help="strict mode for publishing")
    ap.add_argument("--base", default="/", help="URL path the site is served from (default: /)")
    ap.add_argument("--serve", action="store_true", help="serve dist/ after building")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    if not args.base.endswith("/"):
        args.base += "/"
    build(args)
    if args.serve:
        serve(args.port)


if __name__ == "__main__":
    main()
