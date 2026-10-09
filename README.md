# Dienos istorija

Kasdienės istorijos apie geografiją, istoriją ir geopolitiką – [dienosistorija.lt](https://dienosistorija.lt).

- `data/stories/<YYYY-MM-DD>.json` – istorijų tekstai (date, title, category, readMin, hook, emailSummary, body, takeaways, sources)
- `img/` – paveikslėliai iš Wikimedia Commons (`<data>-<n>.jpg`)
- `python3 build.py` – sugeneruoja `index.html` (naujausia istorija), `<data>/index.html`, `archyvas/index.html`, `feed.xml` ir `404.html`
- `style.css` – svetainės stilius

Nauja istorija įkeliama kiekvieną rytą automatiškai: Claude užduotis 5:15 parašo istoriją ir įdeda `<data>.json` į viešą Google Drive aplanką, o GitHub Actions (`.github/workflows/import-story.yml`, kas 10 min. 5:00–9:00) ją paima (`scripts/import_story.py`), atsisiunčia paveikslėlius iš Wikimedia Commons, paskelbia svetainėje ir išsiunčia laišką.

## Rytinis laiškas

Kai į `main` įkeliamas naujas `data/stories/<data>.json`, GitHub Actions (`.github/workflows/send-email.yml`) per Brevo išsiunčia laišką visam sąrašui (`scripts/send_email.py`). Reikalingi saugyklos slapti nustatymai `BREVO_API_KEY` ir `BREVO_LIST_ID`. Bandomąjį laišką galima išsiųsti per **Actions → Rytinis laiškas → Run workflow**.
