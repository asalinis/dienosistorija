# Dienos istorija

Kasdienės istorijos apie geografiją, istoriją ir geopolitiką – [dienosistorija.lt](https://dienosistorija.lt).

- `data/stories/<YYYY-MM-DD>.json` – istorijų tekstai (date, title, category, readMin, hook, body, takeaways, sources)
- `img/` – paveikslėliai iš Wikimedia Commons (`<data>-<n>.jpg`)
- `python3 build.py` – sugeneruoja `index.html`, `<data>/index.html`, `feed.xml` ir `404.html`
- `style.css` – svetainės stilius

Nauja istorija įkeliama kiekvieną rytą automatiškai.
