# Dienos istorija

Kasdienės istorijos apie geografiją, istoriją ir geopolitiką – [dienosistorija.lt](https://dienosistorija.lt).

- `data/stories/<YYYY-MM-DD>.json` – istorijų tekstai (date, title, category, readMin, hook, emailSummary, body, takeaways, sources)
- `img/` – paveikslėliai iš Wikimedia Commons (`<data>-<n>.jpg`)
- `python3 build.py` – sugeneruoja `index.html` (naujausia istorija), `<data>/index.html`, `archyvas/index.html`, `feed.xml` ir `404.html`
- `style.css` – svetainės stilius

Nauja istorija įkeliama kiekvieną rytą automatiškai.

## Rytinis laiškas

Kai į `main` įkeliamas naujas `data/stories/<data>.json`, GitHub Actions (`.github/workflows/send-email.yml`) per Brevo išsiunčia laišką visam sąrašui (`scripts/send_email.py`). Reikalingi saugyklos slapti nustatymai `BREVO_API_KEY` ir `BREVO_LIST_ID`. Bandomąjį laišką galima išsiųsti per **Actions → Rytinis laiškas → Run workflow**.
