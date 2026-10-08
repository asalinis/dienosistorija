#!/usr/bin/env python3
"""Sends the morning email for a story through Brevo.

Usage:
  send_email.py <story.json> [--test email@example.com]

Without --test the email goes to the whole Brevo list (BREVO_LIST_ID).
With --test it is sent only to the given address (must be a Brevo contact).
Needs env: BREVO_API_KEY, BREVO_LIST_ID.
"""
import html
import json
import os
import sys
import urllib.error
import urllib.request

SITE = "https://dienosistorija.lt"
SENDER = {"name": "Dienos istorija", "email": "labas@dienosistorija.lt"}
API = "https://api.brevo.com/v3"
e = html.escape


def call(method, path, body=None):
    req = urllib.request.Request(
        API + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"api-key": os.environ["BREVO_API_KEY"], "content-type": "application/json",
                 "accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = r.read().decode()
            return json.loads(txt) if txt else {}
    except urllib.error.HTTPError as err:
        sys.exit(f"Brevo {method} {path} failed: {err.code} {err.read().decode()}")


def email_html(s):
    url = f"{SITE}/{s['date']}/"
    summary = s.get("emailSummary") or s["hook"]
    paras = "".join(f'<p style="margin:0 0 14px">{e(p.strip())}</p>' for p in summary.split("\n\n") if p.strip())
    return f"""<!doctype html><html lang="lt"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f2f4f3">
<div style="max-width:600px;margin:0 auto;padding:28px 20px;font-family:Georgia,'Times New Roman',serif;font-size:17px;line-height:1.6;color:#16222b">
<p style="margin:0 0 10px;font-family:Menlo,Consolas,monospace;font-size:12px;letter-spacing:.08em;color:#5d6b73">DIENOS ISTORIJA · {e(s['category'].upper())} · ~{e(str(s['readMin']))} MIN.</p>
<h1 style="margin:0 0 16px;font-size:26px;line-height:1.2;font-weight:bold">{e(s['title'])}</h1>
{paras}
<p style="margin:20px 0 26px"><a href="{url}" style="display:inline-block;background:#16222b;color:#ffffff;text-decoration:none;padding:12px 20px;border-radius:3px;font-family:Arial,sans-serif;font-size:15px;font-weight:bold">Skaityti visą istoriją →</a></p>
<p style="margin:0;padding-top:14px;border-top:1px solid #d3dadc;font-family:Menlo,Consolas,monospace;font-size:12px;line-height:1.7;color:#5d6b73">
<a href="{SITE}/archyvas/" style="color:#5d6b73">Visų istorijų archyvas</a> · <a href="{{{{ unsubscribe }}}}" style="color:#5d6b73">Atsisakyti prenumeratos</a></p>
</div></body></html>"""


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    path = args[0]
    test = args[2] if len(args) > 2 and args[1] == "--test" else None
    with open(path, encoding="utf-8") as fh:
        s = json.load(fh)
    list_id = int(os.environ["BREVO_LIST_ID"])
    camp = call("POST", "/emailCampaigns", {
        "name": f"Dienos istorija {s['date']}" + (" (testas)" if test else ""),
        "subject": s["title"],
        "previewText": (s.get("emailSummary") or s["hook"])[:140],
        "sender": SENDER,
        "replyTo": SENDER["email"],
        "htmlContent": email_html(s),
        "recipients": {"listIds": [list_id]},
        "inlineImageActivation": False,
    })
    cid = camp["id"]
    if test:
        call("POST", f"/emailCampaigns/{cid}/sendTest", {"emailTo": [test]})
        print(f"Test email for {s['date']} sent to {test} (campaign {cid})")
    else:
        call("POST", f"/emailCampaigns/{cid}/sendNow")
        print(f"Email for {s['date']} sent to list {list_id} (campaign {cid})")


if __name__ == "__main__":
    main()
