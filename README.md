# Octagon — sito (versione statica)

Sito statico su Vercel (nessuna build) + funzione `api/demo.js` (Resend) per il modulo demo.

- `index.html` home · `pricing.html` listino (`/pricing`) · `reti.html` (`/reti`) · `servizi/<slug>.html` (`/servizi/<slug>`)
- `privacy.html`, `cookie.html`, `termini.html`: generate da `tools/build_legal.py`
- Servizi, pagina Reti, `llms.txt`, `sitemap.xml`, `robots.txt`, JSON-LD e le schede «Cosa fa» della home: generati da `tools/build_pages.py` a partire da `tools/content.py`

Dopo aver modificato i testi in `tools/content.py`:

    python3 tools/build_legal.py && python3 tools/build_pages.py

`SHOW_RETI` in `tools/content.py` accende o spegne pagina e link «Reti di partner».
