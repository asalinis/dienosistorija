#!/usr/bin/env python3
"""Builds the static site from data/stories/*.json.

Each story file: date (YYYY-MM-DD), title, category, readMin, hook,
body (HTML; images as /img/<date>-<n>.jpg), takeaways [3], sources [{title,url}].
Output: index.html, <date>/index.html, feed.xml, 404.html.
"""
import glob
import hashlib
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

SUBSCRIBE = """<section class="sub" id="prenumerata">
<div id="sib-form-container" class="sib-form-container">
<div id="error-message" class="sib-form-message-panel sub-msg sub-err"><div class="sib-form-message-panel__text"><span class="sib-form-message-panel__inner-text">Nepavyko užregistruoti. Patikrinkite el. pašto adresą ir bandykite dar kartą.</span></div></div>
<div id="success-message" class="sib-form-message-panel sub-msg sub-ok"><div class="sib-form-message-panel__text"><span class="sib-form-message-panel__inner-text">Ačiū! Nuo rytojaus Dienos istoriją gausite el. paštu.</span></div></div>
<div id="sib-container">
<form id="sib-form" method="POST" action="https://7ed721d5.sibforms.com/serve/MUIFAAghruBvpt7vhLmCyhsmVP8Fsu63ZJemxWRlHJXgbBMJbajLHLkZily9pJWaa8Is0EeqhF5ihtgmQ-730H3xEmhWiqfIlbcgnSc3nB_5Agk9QFYB9czDIfgSkO0LMA9-5cOWV-Y9JX0k7PtHh_hvRjCzt9CmsElzOJQgS8oVJKlYnxb027abxF_G7wPQtSekTV4Mxt5JhA0Plg==" data-type="subscription">
<h3>Dienos istorija tavo pašto dėžutėje</h3>
<p class="sub-lead">Kiekvieną rytą – trumpa santrauka ir nuoroda į naują istoriją.</p>
<div class="sib-input sib-form-block"><div class="form__entry entry_block"><div class="form__label-row"><div class="entry__field sub-row">
<label class="sub-sr" for="EMAIL">El. pašto adresas</label>
<input class="input" type="email" id="EMAIL" name="EMAIL" autocomplete="email" placeholder="el. pašto adresas" data-required="true" required>
<button class="sib-form-block__button sib-form-block__button-with-loader" form="sib-form" type="submit">Prenumeruoti</button>
</div></div><label class="entry__error entry__error--primary"></label></div></div>
<input type="text" name="email_address_check" value="" class="input--hidden" tabindex="-1" autocomplete="off" aria-hidden="true">
<input type="hidden" name="locale" value="en">
<p class="sub-note">Užsiregistravę sutinkate gauti kasdienį laišką. Atsisakyti galite bet kada – nuoroda yra kiekvieno laiško apačioje.</p>
</form></div></div></section>"""
SUB_SCRIPT = """<script>window.EMAIL_INVALID_MESSAGE=window.SMS_INVALID_MESSAGE=window.GENERIC_INVALID_MESSAGE="Neteisingas el. pašto adresas.";window.REQUIRED_ERROR_MESSAGE="Įveskite el. pašto adresą.";window.INVALID_NUMBER="Neteisingas numeris.";window.INVALID_DATE="Neteisinga data.";window.REQUIRED_CODE_ERROR_MESSAGE="";window.REQUIRED_MULTISELECT_MESSAGE="";window.LOCALE="en";window.translation={common:{selectedList:"",selectedLists:"",selectedOption:"",selectedOptions:""}};var AUTOHIDE=Boolean(0);</script>
<script defer src="https://sibforms.com/forms/end-form/build/main.js"></script>"""

e = html.escape
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css"), "rb") as _f:
    CSS_V = hashlib.md5(_f.read()).hexdigest()[:8]


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
{FONTS}<link rel="stylesheet" href="/style.css?v={CSS_V}">
</head><body><div class="wrap">
<header class="mast"><a class="name" href="/">{NAME}</a><nav class="coord"><a href="/archyvas/">Archyvas</a></nav></header>
<main>{body}</main>{SUBSCRIBE}{FOOT}
</div>{SUB_SCRIPT}</body></html>
"""


def meta_line(s, long=False):
    rm = f"skaitymo laikas ~{s['readMin']} min." if long else f"{s['readMin']} min."
    return f'<div class="label">{e(lt_date(s["date"]))} · <span class="cat">{e(s["category"])}</span> · {e(rm)}</div>'


def story_page(s, newer, older, url=None):
    keep = "".join(f"<li>{e(t)}</li>" for t in s.get("takeaways", []))
    src = "".join(f'<li><a href="{e(x["url"])}" rel="noopener">{e(x.get("title") or x["url"])}</a></li>'
                  for x in s.get("sources", []) if str(x.get("url", "")).startswith("http"))
    left = '<a href="/%s/">← %s</a>' % (older["date"], e(older["title"])) if older else ""
    right = '<a href="/%s/">%s →</a>' % (newer["date"], e(newer["title"])) if newer else ""
    nav = f'<nav class="nav"><span>{left}</span><span>{right}</span></nav>'
    body = f"""<a class="back" href="/archyvas/">Visos istorijos – archyvas →</a>
<article>{meta_line(s, True)}
<h1>{e(s['title'])}</h1>
<p class="hook">{e(s['hook'])}</p>
<div class="body">{s['body']}</div>
{f'<div class="keep"><h3>Trys dalykai, kuriuos verta prisiminti</h3><ol>{keep}</ol></div>' if keep else ''}
{f'<div class="src">Šaltiniai<ul>{src}</ul></div>' if src else ''}
</article>{nav}"""
    return page(f"{s['title']} · {NAME}", s["hook"], url or f"/{s['date']}/", body, first_img(s), "article")


def archive_page(stories):
    items = "".join(f'<li><a href="/{s["date"]}/"><span class="d">{s["date"]}</span>'
                    f'<span class="t">{e(s["title"])}<span class="c">{e(s["category"])}</span></span></a></li>'
                    for s in stories)
    body = (f'<section class="archive"><h3>Archyvas · {len(stories)} istorijos</h3><ol>{items}</ol></section>'
            if stories else '<p class="lead">Istorijų dar nėra.</p>')
    return page(f"Archyvas · {NAME}", "Visos Dienos istorijos: geografija, istorija, geopolitika.", "/archyvas/", body)


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
        if stories:
            fh.write(story_page(stories[0], None, stories[1] if len(stories) > 1 else None, "/"))
        else:
            fh.write(page(NAME, "Kasdienės istorijos apie geografiją, istoriją ir geopolitiką.", "/",
                          '<p class="lead">Pirmoji istorija pasirodys netrukus.</p>'))
    os.makedirs(os.path.join(root, "archyvas"), exist_ok=True)
    with open(os.path.join(root, "archyvas", "index.html"), "w", encoding="utf-8") as fh:
        fh.write(archive_page(stories))
    with open(os.path.join(root, "feed.xml"), "w", encoding="utf-8") as fh:
        fh.write(feed(stories))
    with open(os.path.join(root, "404.html"), "w", encoding="utf-8") as fh:
        fh.write(page(f"Puslapis nerastas · {NAME}", "Puslapis nerastas.", "/404.html",
                      '<p class="lead">Tokio puslapio nėra. <a href="/">Grįžti į pradžią</a></p>'))
    print(f"Built {len(stories)} stories")


if __name__ == "__main__":
    main()
