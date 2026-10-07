"""Lingue del sito: corrispondenza degli indirizzi IT ↔ EN, selettore ITA/ENG, hreflang, segmentazione dei testi.

Usato da build_pages.py (pagine italiane) e da build_en.py (pagine inglesi in /en).
"""
import html, re

SITE = "https://theoctagonai.com"

# slug italiano → slug inglese delle pagine servizio
SERVICE_SLUGS = {
    "automazione": "automation", "shopify": "shopify", "amazon": "amazon",
    "seo-visibilita-ai": "seo-ai-visibility", "analisi": "market-analysis", "social": "social",
    "campagne": "ads", "fotovideo": "photo-video", "clienti": "customer-service", "siti": "websites",
}
PAGES = {"/": "/en", "/pricing": "/en/pricing", "/privacy": "/en/privacy", "/cookie": "/en/cookies", "/termini": "/en/terms"}
PAGES.update({f"/servizi/{a}": f"/en/services/{b}" for a, b in SERVICE_SLUGS.items()})
PAGES_BACK = {v: k for k, v in PAGES.items()}


def en_path(p):
    return PAGES[p]


def full(p):
    return SITE + ("/" if p == "/" else p)


def it_href_to_en(h):
    """Riscrive un link interno italiano nel suo equivalente inglese (ancore e query comprese)."""
    if not h.startswith("/") or h.startswith("//") or h.startswith(("/img/", "/fonts/", "/api/")) or re.match(r"^/[\w.-]+\.(css|js|png|jpg|webp|txt|xml|svg|woff2)$", h):
        return h
    m = re.match(r"^([^?#]*)(\?[^#]*)?(#.*)?$", h)
    path, q, frag = m.group(1) or "/", m.group(2) or "", m.group(3) or ""
    if path not in PAGES:
        raise KeyError(f"link senza equivalente inglese: {h}")
    return PAGES[path] + q + frag


def switcher(it_p, lang):
    en_p = PAGES[it_p]
    cur = lambda l: ' aria-current="true"' if l == lang else ""
    label = "Lingua" if lang == "it" else "Language"
    return (f'<div class="lang" role="group" aria-label="{label}">'
            f'<a href="{it_p}" hreflang="it" lang="it"{cur("it")} aria-label="ITA, Italiano">ITA</a>'
            f'<a href="{en_p}" hreflang="en" lang="en"{cur("en")} aria-label="ENG, English">ENG</a></div>')


def hreflang(it_p):
    en_p = PAGES[it_p]
    return (f'<link rel="alternate" hreflang="it" href="{full(it_p)}">'
            f'<link rel="alternate" hreflang="en" href="{full(en_p)}">'
            f'<link rel="alternate" hreflang="x-default" href="{full(it_p)}">')


def _splice_or_insert(text, start, end, inner, anchor, before=True):
    if start in text:
        a, b = text.index(start) + len(start), text.index(end)
        return text[:a] + inner + text[b:]
    i = text.index(anchor)
    block = start + inner + end
    return text[:i] + block + text[i:] if before else text[:i + len(anchor)] + block + text[i + len(anchor):]


def add_lang(text, it_p, lang="it"):
    """Selettore ITA/ENG prima del pulsante del menu e link hreflang in testa (idempotente)."""
    text = _splice_or_insert(text, "<!-- @lang:start -->", "<!-- @lang:end -->", switcher(it_p, lang), '<a class="btn btn-dark nav-cta"')
    text = _splice_or_insert(text, "<!-- @hreflang:start -->", "<!-- @hreflang:end -->", hreflang(it_p), "</head>")
    return text


# ---------- segmentazione: testi visibili e attributi ----------

TOKEN = re.compile(r"(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|<!--.*?-->|<[^>]+>)", re.S | re.I)
ATTRS = ("alt", "aria-label", "placeholder", "title")
META_TEXT = re.compile(r'<meta\s[^>]*(name|property)="(description|og:title|og:description|twitter:title|twitter:description)"', re.I)
HAS_WORD = re.compile(r"[A-Za-zÀ-ÿ]")


def norm(s):
    return " ".join(s.split())


def segments(text):
    """Restituisce (testi, attributi, script) di una pagina, nell'ordine in cui compaiono."""
    texts, attrs, scripts = [], [], []
    for tok in TOKEN.split(text):
        if not tok:
            continue
        if tok.startswith("<script"):
            scripts.append(tok)
        elif tok.startswith(("<style", "<!--")):
            continue
        elif tok.startswith("<"):
            for name, val in re.findall(r'\s([\w:-]+)="([^"]*)"', tok):
                if (name in ATTRS or (name == "content" and META_TEXT.match(tok))) and HAS_WORD.search(val):
                    attrs.append(norm(val))
        elif HAS_WORD.search(tok):
            texts.append(norm(tok))
    return texts, attrs, scripts


def unescape(s):
    return html.unescape(s)
