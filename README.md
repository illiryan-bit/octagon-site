# Octagon — sito (versione statica)

Sito statico su Vercel (nessuna build) + funzione `api/demo.js` (Resend) per il modulo demo.

- `index.html` home · `pricing.html` listino (`/pricing`) · `reti.html` (`/reti`) · `servizi/<slug>.html` (`/servizi/<slug>`)
- `privacy.html`, `cookie.html`, `termini.html`: generate da `tools/build_legal.py`
- Versione inglese in `en/` (home, listino, `en/services/*`, privacy, cookies, terms): generata da `tools/build_en.py` traducendo le pagine italiane con il dizionario `tools/i18n_en.txt`. Se un testo italiano nuovo non ha traduzione, lo script si ferma e lo elenca. Corrispondenza degli indirizzi, selettore ITA/ENG e hreflang in `tools/i18n.py`
- Servizi, pagina Reti, `llms.txt`, `sitemap.xml`, `robots.txt`, JSON-LD e le schede «Cosa fa» della home: generati da `tools/build_pages.py` a partire da `tools/content.py`

Dopo aver modificato i testi in `tools/content.py`:

    python3 tools/build_legal.py && python3 tools/build_pages.py && python3 tools/build_en.py

`SHOW_RETI` in `tools/content.py` accende o spegne pagina e link «Reti di partner».
