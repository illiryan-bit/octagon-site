#!/usr/bin/env python3
"""Genera la versione inglese del sito in /en a partire dalle pagine italiane già generate.

Uso:  python3 tools/build_legal.py && python3 tools/build_pages.py && python3 tools/build_en.py

Come funziona
  - ogni testo visibile, attributo accessibile (alt, aria-label, placeholder, title) e meta descrizione
    delle pagine italiane viene cercato nel dizionario tools/i18n_en.txt;
  - le stringhe dentro gli script si sostituiscono con le coppie delle sezioni [js:*] dello stesso file;
  - i dati strutturati JSON-LD vengono tradotti campo per campo;
  - link, canonical, hreflang, lingua della pagina e selettore ITA/ENG vengono riscritti per /en.
Se un testo italiano non ha traduzione lo script si ferma e lo elenca: nessuna pagina esce a metà.
"""
from pathlib import Path
from urllib.parse import quote, unquote
import html, json, re, sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import PAGES, SITE, TOKEN, ATTRS, META_TEXT, HAS_WORD, it_href_to_en, add_lang, full, norm
from content import WHATSAPP_TEXT, SERVICES

ROOT = Path(__file__).resolve().parent.parent
WHATSAPP_TEXT_EN = "Hi Octagon, I'd like to know what the system could take on for my business."

SOURCES = [("index.html", "/"), ("pricing.html", "/pricing")] + \
          [(f"servizi/{s['slug']}.html", f"/servizi/{s['slug']}") for s in SERVICES] + \
          [("privacy.html", "/privacy"), ("cookie.html", "/cookie"), ("termini.html", "/termini")]


# ---------- dizionario ----------

def load_dict(path):
    """Formato: riga italiana, riga che inizia con '= ' con l'inglese, riga vuota.
    '@file.html: testo' limita la traduzione a una pagina. Le sezioni [js:nome] contengono sostituzioni
    letterali da applicare agli script ('*' = tutte le pagine). [same] elenca i testi uguali nelle due lingue."""
    text_map, page_map, js, same = {}, {}, {}, set()
    section = "text"
    lines = path.read_text().split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip() or ln.startswith("#"):
            i += 1
            continue
        m = re.match(r"^\[(js:[\w.*/-]+|same|text)\]$", ln.strip())
        if m:
            section = m.group(1)
            i += 1
            continue
        if section == "same":
            same.add(ln.strip())
            i += 1
            continue
        if i + 1 >= len(lines) or not lines[i + 1].startswith("= "):
            raise SystemExit(f"i18n_en.txt riga {i + 1}: manca la riga '= ' dopo «{ln}»")
        it, en = ln, lines[i + 1][2:]
        if section.startswith("js:"):
            js.setdefault(section[3:], []).append((it, en))
        else:
            pm = re.match(r"^@([\w./-]+):\s(.*)$", it)
            if pm:
                page_map[(pm.group(1), norm(pm.group(2)))] = en
            else:
                text_map[norm(it)] = en
        i += 2
    return text_map, page_map, js, same


TEXT, PAGE, JS, SAME = load_dict(Path(__file__).resolve().parent / "i18n_en.txt")
missing = []


def tr(s, page, where="testo"):
    """Traduce un segmento (già con entità HTML) restituendo testo con entità sicure."""
    key = norm(html.unescape(s))
    if not HAS_WORD.search(key):
        return None
    if (page, key) in PAGE:
        return PAGE[(page, key)]
    if key in TEXT:
        return TEXT[key]
    if key in SAME:
        return key
    missing.append((page, where, key))
    return key


def money(s):
    """Formato inglese degli importi: €1.500 → €1,500 · €42,00 → €42.00"""
    s = re.sub(r"€(\d{1,3})\.(\d{3})\b", r"€\1,\2", s)
    return re.sub(r"€(\d+),(\d{2})\b", r"€\1.\2", s)


# ---------- pezzi della pagina ----------

def tr_text(tok, page):
    en = tr(tok, page)
    if en is None:
        return money(tok)
    lead = re.match(r"^\s*", tok).group(0)
    trail = re.search(r"\s*$", tok).group(0)
    if re.match(r"^[,.;:)]", en):
        lead = ""
    return lead + money(html.escape(en, quote=False)) + trail


def rewrite_href(h):
    if h.startswith("https://wa.me/"):
        return h.replace(quote(WHATSAPP_TEXT), quote(WHATSAPP_TEXT_EN))
    if h.startswith("mailto:"):
        return h.replace("Richiesta%20demo", "Demo%20request")
    if not h.startswith("/"):
        return h
    m = re.match(r"^(/[^?#]*)?\?piano=([^#]*)(#.*)?$", h)
    if m:
        plan = unquote(m.group(2))
        en_plan = tr(html.escape(plan), "*", "piano") or plan
        return it_href_to_en((m.group(1) or "/") + "?piano=" + quote(en_plan) + (m.group(3) or ""))
    return it_href_to_en(h)


def tr_tag(tok, page):
    def attr(m):
        name, val = m.group(1), m.group(2)
        if name in ATTRS or (name == "content" and META_TEXT.match(tok)):
            en = tr(val, page, name)
            if en is not None:
                val = html.escape(en)
        elif name == "href":
            val = rewrite_href(html.unescape(val)).replace("&", "&amp;") if "&" in val else rewrite_href(val)
        elif name in ("src", "srcset") and not val.startswith(("/", "http", "data:", "#")):
            val = re.sub(r"(^|,\s*)(img/)", r"\1/img/", val)
        return f' {name}="{val}"'
    tok = re.sub(r'\s([\w:-]+)="([^"]*)"', attr, tok)
    if tok.startswith("<html"):
        tok = tok.replace('lang="it"', 'lang="en"')
    if 'property="og:locale"' in tok:
        tok = tok.replace('content="it_IT"', 'content="en_US"')
    if 'name="lang"' in tok and 'type="hidden"' in tok:
        tok = tok.replace('value="it"', 'value="en"')
    return tok


LD_TEXT = {"name", "description", "text", "category", "serviceType", "unitText", "alternateName"}


def tr_ld(node, page):
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if isinstance(v, str):
                if k in LD_TEXT:
                    v = money(tr(html.escape(v), page, "json-ld " + k) or v)
                elif k in ("url", "item") or (k == "@id" and not v.endswith(("#org", "#site"))):
                    v = url_en(v)
                elif k == "inLanguage":
                    v = "en"
            else:
                v = tr_ld(v, page)
            out[k] = v
        return out
    if isinstance(node, list):
        return [tr_ld(x, page) for x in node]
    return node


def url_en(u):
    if not u.startswith(SITE):
        return u
    rest = u[len(SITE):] or "/"
    m = re.match(r"^([^#]*)(#.*)?$", rest)
    path, frag = m.group(1) or "/", m.group(2) or ""
    return full(PAGES[path]) + frag if path in PAGES else u


def tr_script(tok, page):
    if 'type="application/ld+json"' in tok:
        a = tok.index(">") + 1
        b = tok.rindex("</script>")
        data = tr_ld(json.loads(tok[a:b]), page)
        return tok[:a] + json.dumps(data, ensure_ascii=False) + tok[b:]
    for key in ("*", page):
        for it, en in JS.get(key, []):
            if it not in tok:
                if key == page:
                    missing.append((page, "js", "sostituzione non trovata: " + it))
                continue
            tok = tok.replace(it, en)
    return money(tok)


def strip_block(text, start, end):
    if start in text:
        a, b = text.index(start), text.index(end) + len(end)
        text = text[:a] + text[b:]
    return text


def translate(text, src, it_p):
    page = src.split("/")[-1]
    text = strip_block(text, "<!-- @lang:start -->", "<!-- @lang:end -->")
    text = strip_block(text, "<!-- @hreflang:start -->", "<!-- @hreflang:end -->")
    out = []
    for tok in TOKEN.split(text):
        if not tok:
            continue
        if tok.startswith("<script"):
            a = tok.index(">") + 1
            out.append(tr_tag(tok[:a], page) + tr_script(tok, page)[a:])
        elif tok.startswith(("<style", "<!--")):
            out.append(tok)
        elif tok.startswith("<"):
            out.append(tr_tag(tok, page))
        else:
            out.append(tr_text(tok, page))
    text = "".join(out)
    # canonical e og:url puntano alla pagina inglese
    text = re.sub(r'(<link rel="canonical" href=")([^"]+)(")', lambda m: m.group(1) + url_en(m.group(2)) + m.group(3), text)
    text = re.sub(r'(<meta property="og:url" content=")([^"]+)(")', lambda m: m.group(1) + url_en(m.group(2)) + m.group(3), text)
    if 'rel="canonical"' not in text:
        text = text.replace("</title>", f'</title>\n<link rel="canonical" href="{full(PAGES[it_p])}">', 1)
    return add_lang(text, it_p, "en")


def out_file(en_p):
    rel = "en/index.html" if en_p == "/en" else en_p.lstrip("/") + ".html"
    return ROOT / rel


LEFTOVER = re.compile(r"\b(il|lo|la|gli|le|della|dello|degli|delle|nel|nella|sono|che|perché|questo|questa|anche|ogni|tuo|tua|tuoi|noi|siamo|servizi|prenota|listino|richiesta|lavoro|negozio|giorno|orario|scegli|grazie|invio|riprova|fermata|approvata|rifiutata|prezzo|campagna|settimana)\b", re.I)


def leftovers(text):
    """Controllo di sicurezza: parole italiane frequenti rimaste nel testo visibile o negli script."""
    found = []
    body = re.sub(r"<style\b.*?</style>|<script type=\"application/ld\+json\">.*?</script>", "", text, flags=re.S)
    for tok in TOKEN.split(body):
        if not tok or tok.startswith(("<!--", "<style")):
            continue
        if tok.startswith("<script"):
            for s in re.findall(r"'((?:[^'\\\n]|\\.)*)'|`((?:[^`\\]|\\.)*)`|\"((?:[^\"\\\n]|\\.)*)\"", tok):
                s = next((x for x in s if x), "")
                if " " in s and LEFTOVER.search(s) and not re.search(r"[{}();=]|class=|viewBox|polygon", s):
                    found.append("js: " + s[:120])
            continue
        if tok.startswith("<"):
            for name, val in re.findall(r'\s([\w:-]+)="([^"]*)"', tok):
                if name in ATTRS + ("content",) and LEFTOVER.search(val) and " " in val:
                    found.append(f"{name}: {val[:120]}")
            continue
        if LEFTOVER.search(tok) and " " in tok.strip():
            found.append(norm(tok)[:120])
    return found


def write_llms():
    """Aggiunge a llms.txt la sezione in inglese, con gli indirizzi /en (idempotente)."""
    from content import AREAS, services_in
    t = lambda x: TEXT.get(norm(x), x)
    f = ROOT / "llms.txt"
    base = f.read_text().split("\n## English")[0].rstrip("\n")
    lines = ["", "## English", "",
             "> Octagon is a founder-led studio that builds and runs AI agent systems for the operational work of companies and brands, "
             "from the independent store to the international brand with distributors and retail locations. The system prepares the work; "
             "every action that matters goes out only after a person approves it on Telegram.", "",
             "The system runs 46 workflows (38 active every day) and 8 AI agents on infrastructure managed by Octagon. "
             "Rules written in code, such as a minimum price or a spending limit, stop out-of-bounds proposals before they reach the person.", ""]
    for key, name, _ in AREAS:
        lines.append(f"### {t(name)}")
        for s in services_in(key):
            ok = f"Approval required: {t(s['you'])[0].lower() + t(s['you'])[1:]}" if s["ok"] else "Read-only: no actions taken."
            lines.append(f"- [{t(s['name'])}]({full(PAGES['/servizi/' + s['slug']])}): {t(s['what'])} {ok}")
        lines.append("")
    lines += [f"- [Pricing]({full('/en/pricing')}): Starter (€599 setup, then €99/month, 5 active workflows), Growth (€1,500, then €299/month, 15 workflows), "
              "Scale (€2,499, then €499/month, 24 workflows), Enterprise (from €3,999, custom monthly fee, 38 workflows). Prices exclude VAT. "
              "Monthly add-ons; websites and stores by project: landing page €799, Shopify store €1,500, custom application on quote.",
              f"- Book a demo: {full('/en')}#demo",
              f"- [Privacy]({full('/en/privacy')}) · [Cookies]({full('/en/cookies')}) · [Terms]({full('/en/terms')})", ""]
    f.write_text(base + "\n" + "\n".join(lines))


if __name__ == "__main__":
    written, warn = [], []
    for src, it_p in SOURCES:
        en_text = translate((ROOT / src).read_text(), src, it_p)
        dest = out_file(PAGES[it_p])
        written.append((dest, en_text))
        warn += [(src, w) for w in leftovers(en_text)]
    if missing:
        seen = set()
        for page, where, key in missing:
            if (where, key) in seen:
                continue
            seen.add((where, key))
            print(f"MANCA [{page} · {where}] {key}")
        raise SystemExit(f"\n{len(seen)} testi senza traduzione: nessun file scritto.")
    for dest, text in written:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)
    write_llms()
    for src, w in warn:
        print(f"CONTROLLA [{src}] {w}")
    print(f"Generate {len(written)} pagine inglesi in /en", "· parole italiane sospette: " + str(len(warn)))
