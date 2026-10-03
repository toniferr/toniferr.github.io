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
import math
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
    """Escape, then allow **bold**, *em* and `code`."""
    out = esc(text)
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


# --------------------------------------------------------------------------- star charts
# Project diagrams are drawn as star charts: every node is a star at the centre of its grid box,
# edges are constellation lines and groups are dashed constellation boundaries, as in a printed atlas.

SERIF_W = 7.8   # approx. Cormorant Garamond italic advance per char at 19px
SUB_W = 7.4     # approx. JetBrains Mono advance per char at 10.5px with letter-spacing


def node_box(n: dict) -> tuple[float, float, float, float]:
    return n["x"] * UNIT, n["y"] * UNIT, n.get("w", 8) * UNIT, n.get("h", NODE_H) * UNIT


def node_centre(n: dict) -> tuple[float, float]:
    x, y, w, h = node_box(n)
    return x + w / 2, y + h / 2


def star_symbol(kind: str, accent: bool) -> str:
    """Chart symbols: external systems are galaxies, data stores planetary nebulae, users observers."""
    if kind == "external":
        return ('<ellipse class="st-galaxy" rx="9" ry="3.8" transform="rotate(-25)"/>'
                '<circle class="st-core" r="1.8"/>')
    if kind == "db":
        return '<circle class="st-ring" r="7.5"/><circle class="st-core" r="2.8"/>'
    if kind == "user":
        return '<path class="st-spikes" d="M-9 0H9M0-9V9"/><circle class="st-core" r="2.6"/>'
    r = 6.2 if accent else 4.2
    return f'<circle class="st-glow" r="{r * 3:.1f}"/><circle class="st-core" r="{r}"/>'


def render_diagram(spec: dict, lang: str, uid: str, title: str, extra_class: str = "") -> str:
    W, H = spec["cols"] * UNIT, spec["rows"] * UNIT
    nodes = {n["id"]: n for n in spec["nodes"]}
    o = [f'<svg class="dg {extra_class}" viewBox="-10 -10 {W + 20} {H + 20}" role="img" '
         f'aria-labelledby="{uid}-t" data-uid="{uid}">',
         f'<title id="{uid}-t">{esc(title)}</title>']

    for i, g in enumerate(spec.get("groups", [])):
        x, y, w, h = g["x"] * UNIT, g["y"] * UNIT, g["w"] * UNIT, g["h"] * UNIT
        label = loc(g.get("label", ""), lang)
        o.append(f'<g class="dg-group" data-i="{i}"><rect class="dg-group-box" x="{x}" y="{y}" width="{w}" '
                 f'height="{h}" rx="22"/><text class="dg-group-label" x="{x + 16}" y="{y + 20}">{esc(label)}</text></g>')

    for i, e in enumerate(spec["edges"]):
        (ax, ay), (bx, by) = node_centre(nodes[e["from"]]), node_centre(nodes[e["to"]])
        dx, dy = bx - ax, by - ay
        length = (dx * dx + dy * dy) ** 0.5 or 1
        ux, uy = dx / length, dy / length
        x1, y1, x2, y2 = ax + ux * 11, ay + uy * 11, bx - ux * 11, by - uy * 11  # stop short of the stars
        d = f"M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}"
        o.append(f'<g class="dg-edge-g" data-from="{e["from"]}" data-to="{e["to"]}" data-i="{i}">'
                 f'<path class="dg-edge" d="{d}" pathLength="1"/><path class="dg-flow" d="{d}"/>')
        if e.get("label"):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            o.append(f'<text class="dg-elabel" x="{mx:.1f}" y="{my - 6:.1f}">{esc(loc(e["label"], lang))}</text>')
        o.append("</g>")

    for i, n in enumerate(spec["nodes"]):
        x, y, w, h = node_box(n)
        cx, cy = node_centre(n)
        kind = n.get("kind", "service")
        label, sub = loc(n["label"], lang), loc(n.get("sub", ""), lang)
        pos = n.get("labelPos", "below")
        if pos in ("below", "above") and max(len(label) * SERIF_W, len(sub) * SUB_W) > w + 20:
            warn(f"chart {uid}: label of star '{n['id']}' is wider than its box ({label!r} in {w:.0f}px)")
        anchor = {"below": "middle", "above": "middle", "right": "start", "left": "end"}[pos]
        lx = {"below": 0, "above": 0, "right": 15, "left": -15}[pos]
        ly = {"below": 29, "above": -32 if sub else -18, "right": sub and -2 or 5, "left": sub and -2 or 5}[pos]
        cls = f"dg-node kind-{kind}" + (" accent" if n.get("accent") else "")
        texts = f'<text class="dg-label" x="{lx}" y="{ly}" text-anchor="{anchor}">{esc(label)}</text>'
        if sub:
            texts += f'<text class="dg-sub" x="{lx}" y="{ly + 16}" text-anchor="{anchor}">{esc(sub)}</text>'
        o.append(f'<g class="{cls}" data-id="{n["id"]}" data-i="{i}" transform="translate({cx:.0f} {cy:.0f})">'
                 f'{star_symbol(kind, bool(n.get("accent")))}{texts}</g>')
    o.append("</svg>")
    return "".join(o)


def render_constellation(spec: dict, lang: str, title: str) -> str:
    """The hero: one star per section, joined by constellation lines; every star is a link."""
    W, H = spec["width"], spec["height"]
    stars = {st["id"]: st for st in spec["stars"]}
    o = [f'<svg class="constellation" viewBox="0 0 {W} {H}" role="img" aria-labelledby="cs-t">',
         f'<title id="cs-t">{esc(title)}</title>',
         # decorative celestial grid: two meridians and a parallel, like an atlas plate
         '<g class="cs-grid" aria-hidden="true">'
         f'<path d="M-40 {H * .78:.0f} Q {W / 2:.0f} {H * .52:.0f} {W + 40} {H * .7:.0f}"/>'
         f'<path d="M{W * .22:.0f} -20 Q {W * .3:.0f} {H / 2:.0f} {W * .18:.0f} {H + 20}"/>'
         f'<path d="M{W * .68:.0f} -20 Q {W * .6:.0f} {H / 2:.0f} {W * .74:.0f} {H + 20}"/>'
         '</g>']
    for i, (a, b) in enumerate(spec["lines"]):
        sa, sb = stars[a], stars[b]
        o.append(f'<line class="cs-line" data-a="{a}" data-b="{b}" data-i="{i}" x1="{sa["x"]}" y1="{sa["y"]}" '
                 f'x2="{sb["x"]}" y2="{sb["y"]}" pathLength="1"/>')
    for i, st in enumerate(spec["stars"]):
        r = max(2.4, 8 - 2.1 * st["mag"])
        label, sub = loc(st["label"], lang), loc(st.get("sub", ""), lang)
        spikes = (f'<path class="cs-spikes" d="M{-r * 4:.1f} 0H{r * 4:.1f}M0 {-r * 4:.1f}V{r * 4:.1f}"/>'
                  if st["mag"] < 1.2 else "")
        o.append(
            f'<a class="cs-link" href="{esc(st["href"])}" aria-label="{esc(st["greek"])} {esc(label)}">'
            f'<g class="cs-star" data-id="{st["id"]}" data-i="{i}" transform="translate({st["x"]} {st["y"]})">'
            f'<circle class="cs-hit" r="34"/><circle class="cs-halo" r="{r * 4.5:.1f}"/>{spikes}'
            f'<circle class="cs-core" r="{r:.1f}"/>'
            f'<text class="cs-greek" x="{r + 8:.0f}" y="{-r - 4:.0f}">{esc(st["greek"])}</text>'
            f'<text class="cs-name" x="{r + 8:.0f}" y="{r + 16:.0f}">{esc(label)}</text>'
            + (f'<text class="cs-sub" x="{r + 8:.0f}" y="{r + 31:.0f}">{esc(sub)}</text>' if sub else "")
            + '</g></a>')
    o.append(f'<text class="cs-title" x="{W - 8}" y="{H - 14}" text-anchor="end">{esc(spec["name"].upper())}</text>')
    o.append("</svg>")
    return "".join(o)


ROMAN = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
         (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


def roman(n: int) -> str:
    out = ""
    for v, sym in ROMAN:
        while n >= v:
            out += sym
            n -= v
    return out


# --------------------------------------------------------------------------- page helpers


def section_head(sid: str, no: int, ui: dict, title: str, intro: str | None = None) -> str:
    label = ui["nav"][sid]
    return (f'<header class="sheet-head reveal">'
            f'<p class="sheet-label"><span class="sheet-no">{roman(no)}</span><span>{esc(label)}</span></p>'
            f'<h2 id="{sid}-h">{md(title)}</h2>'
            + (f'<p class="sheet-intro">{md(intro)}</p>' if intro else "")
            + f'<span class="sheet-ref" aria-hidden="true">{esc(ui["titleblock"]["plate"])} {roman(no)} · '
              f'{roman(dt.date.today().year)}</span>'
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
    chart = render_constellation(c["hero"], lang, h["diagramLabel"])
    first, _, rest = p["name"].partition(" ")
    return f"""
<section class="hero" id="top" aria-labelledby="hero-name">
  <div class="hero-text">
    <p class="kicker"><span class="kicker-star" aria-hidden="true">✦</span>{esc(h['kicker'])}</p>
    <p class="coords" aria-hidden="true">{esc(h['coords'])}</p>
    <h1 id="hero-name"><span class="greet">{esc(h['greeting'])}</span>
      <span class="name"><span class="name-line">{esc(first)}</span> <span class="name-line">{esc(rest)}</span></span>
    </h1>
    <p class="lead">{md(fmt(h['lead'], years=years))}</p>
    <div class="cta">
      <a class="btn btn-primary" href="#projects">{esc(h['ctaProjects'])}</a>
      <a class="btn" href="#contact">{esc(h['ctaContact'])}</a>
    </div>
  </div>
  <figure class="hero-chart">
    {chart}
    <figcaption>{esc(h['diagramHint'])}</figcaption>
  </figure>
  <div class="cartouche" aria-hidden="true">
    <span class="c-plate">{esc(t['plate'])} I</span>
    <span class="c-title">{esc(c['hero']['name'])}</span>
    <span class="c-sub">{esc(loc(c['hero']['meaning'], lang))} · {esc(t['chart'])} {esc(p['name'])} · {esc(t['epoch'])} {dt.date.today():%Y.%m}</span>
  </div>
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
        <span class="reticle" aria-hidden="true"></span>
      </div>
      <figcaption><span>OBS. I</span><span>{esc(c['profile']['location'][lang])}</span></figcaption>
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
        r = idx.get(p.get("repo", "").lower(), {})
        meta = []
        if r:
            meta.append(f'<li>{icon("star")}<span><strong>{r["stars"]}</strong> {esc(pu["stars"])}</span></li>')
            meta.append(f'<li>{icon("clock")}<span>{esc(pu["updated"])} {esc(fmt_date(r["pushed_at"], ui))}</span></li>')
            meta.append(f'<li>{icon("flag")}<span>{esc(pu["since"])} {r["created_at"][:4]}</span></li>')
            if r.get("license") and r["license"] != "NOASSERTION":
                meta.append(f'<li>{icon("scale")}<span>{esc(r["license"])}</span></li>')
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
            actions.append(f'<a class="btn btn-sm btn-primary" href="{esc(links["demo"])}">{icon("ext")}{esc(pu["demo"])}</a>')
        if links.get("download"):
            actions.append(f'<a class="btn btn-sm btn-primary" href="{esc(links["download"])}">{icon("download")}{esc(pu["download"])}</a>')
        diagram = ""
        if p.get("diagram"):
            diagram = (f'<figure class="project-diagram">'
                       f'{render_diagram(p["diagram"], lang, "p-" + p["id"], fmt(pu["diagram"], name=p["title"]))}'
                       f'<figcaption>TF {n} · {esc(p["title"])}</figcaption></figure>')
        lang_bar = render_repo_languages(r.get("languages", {})) if r else ""
        arts.append(f"""
  <article class="project reveal{' flip' if n % 2 == 0 else ''}" id="project-{esc(p['id'])}" aria-labelledby="project-{esc(p['id'])}-h">
    <div class="project-text">
      <p class="project-no">TF {n}</p>
      <h3 id="project-{esc(p['id'])}-h">{esc(p['title'])}</h3>
      <p class="tagline">{md(loc(p['tagline'], lang))}</p>
      <ul class="meta">{''.join(meta)}</ul>
      <p class="summary">{md(loc(p['summary'], lang))}</p>
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
        cards = "".join(render_card(p["title"], loc(p["tagline"], lang), p.get("repo"), p.get("links", {}).get("demo"),
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
        items.append(f"""
    <li class="tl-item track-{e['track']}{' is-draft' if e.get('draft') else ''}{' is-current' if e.get('current') else ''} reveal">
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
    legend = "".join(f'<li class="track-{k}"><span aria-hidden="true"></span>{esc(v)}</li>' for k, v in tracks.items())
    return f"""
<section class="sheet" id="career" aria-labelledby="career-h">
  {section_head('career', 4, ui, cu['title'], cu['intro'])}
  <ul class="tl-legend reveal">{legend}</ul>
  <ol class="timeline">{''.join(items)}</ol>
</section>"""


def render_orrery(layers: list, lang: str, sun: str) -> str:
    """The architecture is the sun; each stack layer orbits it. Planets are moved by main.js."""
    o = ['<svg class="orrery" viewBox="-250 -132 500 264" aria-hidden="true">']
    planets = []
    for n, layer in enumerate(layers, 1):
        rx = 62 + (n - 1) * 34
        ry = rx * .5
        angle = (n * 137.5) % 360  # golden angle, so planets start spread out
        px, py = rx * math.cos(math.radians(angle)), ry * math.sin(math.radians(angle))
        o.append(f'<ellipse class="orbit s{n}" data-layer="{esc(layer["id"])}" rx="{rx}" ry="{ry:.1f}"/>')
        planets.append(f'<g class="planet s{n}" data-layer="{esc(layer["id"])}" data-rx="{rx}" data-ry="{ry:.1f}" '
                       f'data-angle="{angle:.1f}" data-period="{24 + n * 9}" transform="translate({px:.1f} {py:.1f})">'
                       f'<circle r="{5 + (n % 3)}"/><text x="10" y="4">L{n}</text></g>')
    o.append('<circle class="sun-glow" r="46"/><circle class="sun" r="20"/>')
    o += planets
    o.append(f'<text class="sun-label" y="44" text-anchor="middle">{esc(sun)}</text></svg>')
    return "".join(o)


def render_stack(c: dict, lang: str, ui: dict) -> str:
    su = ui["stack"]
    s = c["skills"]
    cross = s["crosscut"]
    cross_items = "".join(f"<li>{esc(loc(i, lang))}</li>" for i in cross["items"])
    layers = []
    for n, layer in enumerate(s["layers"], 1):
        chips = "".join(f"<li>{esc(loc(i, lang))}</li>" for i in layer["items"])
        layers.append(f'<li class="layer s{n} reveal" data-layer="{esc(layer["id"])}">'
                      f'<p class="layer-name"><span class="sw s{n}" aria-hidden="true"></span>'
                      f'<span class="layer-no">L{n}</span>{esc(loc(layer["label"], lang))}</p>'
                      f'<ul class="chips">{chips}</ul></li>')
    return f"""
<section class="sheet" id="stack" aria-labelledby="stack-h">
  {section_head('stack', 5, ui, su['title'], su['intro'])}
  <div class="layers">
    <div class="system reveal">
      {render_orrery(s['layers'], lang, loc(cross['label'], lang))}
      <div class="crosscut">
        <p class="crosscut-label"><span>{esc(loc(cross['label'], lang))}</span><small>{esc(su['crosscut'])}</small></p>
        <ul>{cross_items}</ul>
      </div>
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
        rects.append(f'<circle class="hm l{d["level"]}" cx="{x + cell / 2}" cy="{y + cell / 2}" '
                     f'r="{(1.3, 2.4, 3.4, 4.4, 5.6)[d["level"]]}" data-tip="{esc(tip)}"/>')
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


def render_contact(c: dict, lang: str, ui: dict) -> str:
    cu = ui["contact"]
    p = c["profile"]
    return f"""
<section class="sheet contact" id="contact" aria-labelledby="contact-h">
  {section_head('contact', 7, ui, cu['title'], cu['body'])}
  <ul class="contact-list reveal">
    <li><a class="contact-item js-mail" href="{esc(p['links']['linkedin'])}" data-u="{esc(p['email']['user'])}" data-d="{esc(p['email']['domain'])}">
      {icon('mail')}<span><small>{esc(cu['email'])}</small><span class="js-mail-text">{esc(p['email']['user'])} [at] {esc(p['email']['domain'])}</span></span></a></li>
    <li><a class="contact-item" href="{esc(p['links']['linkedin'])}">{icon('linkedin')}<span><small>{esc(cu['linkedin'])}</small>antonio-ferreiro-couto</span></a></li>
    <li><a class="contact-item" href="{esc(p['links']['github'])}">{icon('github')}<span><small>{esc(cu['github'])}</small>@{esc(p['github']['user'])}</span></a></li>
  </ul>
</section>"""


def render_footer(c: dict, ui: dict) -> str:
    f = ui["footer"]
    p = c["profile"]
    return f"""
<footer class="footer">
  <p>© {dt.date.today().year} {esc(p['name'])}. {esc(f['built'])}</p>
  <p class="footer-links"><a href="https://github.com/{esc(p['sourceRepo'])}">{icon('code')}{esc(f['source'])}</a>
    <a href="#top">{icon('arrow-up')}{esc(f['top'])}</a></p>
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
        '<canvas class="sky" aria-hidden="true"></canvas>',
        render_nav(c, lang, ui, base),
        '<main id="main">',
        render_hero(c, lang, ui),
        render_about(c, lang, ui, gh, base),
        render_projects(c, lang, ui, gh),
        render_career(c, lang, ui, release),
        render_stack(c, lang, ui),
        render_github(c, lang, ui, gh),
        render_contact(c, lang, ui),
        "</main>",
        render_footer(c, ui),
        '<div class="readout" aria-hidden="true"><span class="rx">AR 00h 00m</span><span class="ry">Dec +00° 00′</span></div>',
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
        "font_preload": f"{base}assets/fonts/cormorant-garamond.woff2",
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
