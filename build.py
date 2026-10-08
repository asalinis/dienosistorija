#!/usr/bin/env python3
"""Builds the static site from data/stories/*.json.

Each story file: date (YYYY-MM-DD), title, category, readMin, hook,
body (HTML; images as /img/<date>-<n>.jpg), takeaways [3], sources [{title,url}].
Output: index.html, <date>/index.html, feed.xml, 404.html.
"""
import glob
import html
import json
import os
from email.utils import format_datetime
from datetime import datetime, timezone

SITE = "https://dienosistorija.lt"
NAME = "Dienos istorija"
TAGLINE = "Geografija · istorija · geopolitika"
MONTHS = ["sausio", "vasario", "kovo", "balandžio", "gegužės", "birželio", "liepos",
          "rugpjūčio", "rugsėjo", "spalio", "lapkričio", "gruodžio"]
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700'
         '&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&family=IBM+Plex+Mono:wght@400;500&display=swap">')
FOOT = ('<footer class="foot">Nauja istorija kiekvieną rytą. Tekstus rengia dirbtinis intelektas (Claude), '
        'vaizdai – Wikimedia Commons, autoriai ir licencijos nurodyti po kiekvienu. '
        '<a href="/feed.xml">RSS</a></footer>')

e = html.escape


def lt_date(d):
    y, m, dd = d.split("-")
    return f"{y} m. {MONTHS[int(m) - 1]} {int(dd)} d."


def first_img(s):
    b = s.get("body", "")
    i = b.find('src="/img/')
    if i < 0:
        return None
    return b[i + 5:b.find('"', i + 5)]


def page(title, desc, url, body, image=None, kind="website"):
    og_img = f'<meta property="og:image" content="{SITE}{e(image)}">' if image else ""
    return f"""<!doctype html>
<html lang="lt"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:type" content="{kind}"><meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{SITE}{e(url)}">
{og_img}<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{NAME}" href="/feed.xml">
{FONTS}<link rel="stylesheet" href="/style.css">
</head><body><div class="wrap">
<header class="mast"><a class="name" href="/">{NAME}</a><span class="coord">{TAGLINE}</span></header>
<main>{body}</main>{FOOT}
</div></body></html>
"""


def meta_line(s, long=False):
    rm = f"skaitymo laikas ~{s['readMin']} min." if long else f"{s['readMin']} min."
    return f'<div class="label">{e(lt_date(s["date"]))} · <span class="cat">{e(s["category"])}</span> · {e(rm)}</div>'


def story_page(s, newer, older):
    keep = "".join(f"<li>{e(t)}</li>" for t in s.get("takeaways", []))
    src = "".join(f'<li><a href="{e(x["url"])}" rel="noopener">{e(x.get("title") or x["url"])}</a></li>'
                  for x in s.get("sources", []) if str(x.get("url", "")).startswith("http"))
    left = '<a href="/%s/">← %s</a>' % (older["date"], e(older["title"])) if older else ""
    right = '<a href="/%s/">%s →</a>' % (newer["date"], e(newer["title"])) if newer else ""
    nav = f'<nav class="nav"><span>{left}</span><span>{right}</span></nav>'
    body = f"""<a class="back" href="/">← Visos istorijos</a>
<article>{meta_line(s, True)}
<h1>{e(s['title'])}</h1>
<p class="hook">{e(s['hook'])}</p>
<div class="body">{s['body']}</div>
{f'<div class="keep"><h3>Trys dalykai, kuriuos verta prisiminti</h3><ol>{keep}</ol></div>' if keep else ''}
{f'<div class="src">Šaltiniai<ul>{src}</ul></div>' if src else ''}
</article>{nav}"""
    return page(f"{s['title']} · {NAME}", s["hook"], f"/{s['date']}/", body, first_img(s), "article")


def index_page(stories):
    if not stories:
        return page(NAME, "Kasdienės istorijos apie geografiją, istoriją ir geopolitiką.", "/",
                    '<p class="lead">Pirmoji istorija pasirodys netrukus.</p>')
    first, rest = stories[0], stories[1:]
    img = first_img(first)
    lead = f"""<section class="lead">{meta_line(first)}
<h2><a href="/{first['date']}/">{e(first['title'])}</a></h2>
{f'<a href="/{first["date"]}/"><img src="{e(img)}" alt=""></a>' if img else ''}
<p>{e(first['hook'])}</p><a class="read" href="/{first['date']}/">Skaityti →</a></section>"""
    arch = ""
    if rest:
        items = "".join(f'<li><a href="/{s["date"]}/"><span class="d">{s["date"]}</span>'
                        f'<span class="t">{e(s["title"])}<span class="c">{e(s["category"])}</span></span></a></li>'
                        for s in rest)
        arch = f'<section class="archive"><h3>Archyvas · {len(rest)}</h3><ol>{items}</ol></section>'
    return page(NAME, "Kasdienės istorijos apie geografiją, istoriją ir geopolitiką: viena tema, iki 10 minučių skaitymo.",
                "/", lead + arch, img)


def feed(stories):
    items = ""
    for s in stories[:30]:
        dt = datetime.strptime(s["date"], "%Y-%m-%d").replace(hour=5, tzinfo=timezone.utc)
        items += (f"<item><title>{e(s['title'])}</title><link>{SITE}/{s['date']}/</link>"
                  f"<guid>{SITE}/{s['date']}/</guid><pubDate>{format_datetime(dt)}</pubDate>"
                  f"<category>{e(s['category'])}</category><description>{e(s['hook'])}</description></item>")
    return (f'<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel><title>{NAME}</title>'
            f"<link>{SITE}/</link><description>{TAGLINE}</description><language>lt</language>{items}</channel></rss>\n")


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    stories = []
    for f in glob.glob(os.path.join(root, "data", "stories", "*.json")):
        with open(f, encoding="utf-8") as fh:
            stories.append(json.load(fh))
    stories.sort(key=lambda s: s["date"], reverse=True)
    for i, s in enumerate(stories):
        d = os.path.join(root, s["date"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(story_page(s, stories[i - 1] if i > 0 else None, stories[i + 1] if i + 1 < len(stories) else None))
    with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(index_page(stories))
    with open(os.path.join(root, "feed.xml"), "w", encoding="utf-8") as fh:
        fh.write(feed(stories))
    with open(os.path.join(root, "404.html"), "w", encoding="utf-8") as fh:
        fh.write(page(f"Puslapis nerastas · {NAME}", "Puslapis nerastas.", "/404.html",
                      '<p class="lead">Tokio puslapio nėra. <a href="/">Grįžti į pradžią</a></p>'))
    print(f"Built {len(stories)} stories")


if __name__ == "__main__":
    main()
