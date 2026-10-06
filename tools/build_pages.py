#!/usr/bin/env python3
"""Genera le pagine servizio, la pagina Reti di partner e i file per motori di ricerca e assistenti AI.

Uso:  python3 tools/build_pages.py

Scrive:
  servizi/<slug>.html (10)       una pagina per servizio, testi da tools/content.py
  reti.html                      se SHOW_RETI è True
  index.html                     solo il blocco tra <!-- @services:start --> e <!-- @services:end -->
                                 e il JSON-LD tra <!-- @jsonld:start --> e <!-- @jsonld:end -->
  sitemap.xml, robots.txt, llms.txt
"""
from pathlib import Path
from urllib.parse import quote
import html, json, re, sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content import (WHATSAPP, WHATSAPP_TEXT, SITE, EMAIL, SHOW_RETI, AREA_SERVED, AREAS, SERVICES, RETI, HOME_FAQ, area, services_in)
from build_legal import LOGO, foot_bottom, PAGINE

ROOT = Path(__file__).resolve().parent.parent
E = html.escape


def nav_links(prefix=""):
    links = [("/#settimana", "La tua settimana"), ("/#ciclo", "Come funziona"), ("/#cancello", "Il controllo"),
             ("/#aree", "Cosa fa"), ("/#sistema", "Tecnologia"), ("/pricing", "Listino")]
    if SHOW_RETI:
        links.append(("/reti", "Reti di partner"))
    return links


def chrome(path, title, desc, main, jsonld, extra_css=True):
    url = SITE + path
    cur = lambda h: ' aria-current="page"' if h == path else ""
    nav = "\n      ".join(f'<a href="{h}"{cur(h)}>{t}</a>' for h, t in nav_links())
    sheet = "\n  ".join(f'<a class="l" href="{h}"{cur(h)}>{t}</a>' for h, t in nav_links())
    legal_nav = "".join(f'<li><a href="{p}">{n}</a></li>' for p, n in PAGINE)
    serv_nav = "".join(f'<li><a href="/servizi/{s["slug"]}"{cur("/servizi/" + s["slug"])}>{E(s["short"])}</a></li>' for s in SERVICES)
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in jsonld)
    return f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 100 100%27%3E%3Cpolygon points=%2729.3,0 70.7,0 100,29.3 100,70.7 70.7,100 29.3,100 0,70.7 0,29.3%27 fill=%27%231F7A74%27/%3E%3C/svg%3E">
<meta property="og:type" content="website"><meta property="og:site_name" content="Octagon"><meta property="og:locale" content="it_IT"><meta property="og:url" content="{url}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:image" content="{SITE}/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F4EFE8">
<style>[hidden]{{display:none!important}}body{{margin:0}}</style>
<link rel="preload" href="/fonts/public-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/bricolage-grotesque-opsz.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/fonts/fonts.css">
<link rel="stylesheet" href="/legal.css">
<link rel="stylesheet" href="/services.css">
{ld}
</head>
<body id="top">
<a class="skip" href="#contenuto">Vai al contenuto</a>
<header class="nav" id="nav">
  <div class="wrap nav-in">
    <a class="logo" href="/#top" aria-label="Octagon, vai alla home">{LOGO}octagon</a>
    <nav class="links" aria-label="Principale">
      {nav}
    </nav>
    <a class="btn btn-dark nav-cta" href="/#demo">Prenota una demo <span class="arr" aria-hidden="true">→</span></a>
    <button class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="sheet" aria-label="Apri il menu"><span></span></button>
  </div>
</header>
<div class="sheet" id="sheet" hidden>
  {sheet}
  <a class="btn btn-primary" href="/#demo">Prenota una demo <span class="arr" aria-hidden="true">→</span></a>
</div>

<main id="contenuto">
{main}
</main>

<footer aria-labelledby="ft-h">
  <div class="wrap">
    <h2 class="sr" id="ft-h">Informazioni su Octagon</h2>
    <div class="foot">
      <div class="foot-brand">
        <a class="logo" href="/#top" aria-label="Octagon, vai alla home">{LOGO}octagon</a>
        <p class="foot-claim">Il lavoro che si ripete.<br>Lo esegue l'AI.<br><span>Lo approvi tu.</span></p>
        <p>Octagon è uno studio founder-led. Costruiamo e gestiamo sistemi di agenti AI che si occupano del lavoro operativo di aziende e brand, in Italia e nel mondo: ogni azione che conta passa da una tua approvazione.</p>
      </div>
      <nav aria-label="Servizi"><h3>Servizi</h3><ul>{serv_nav}</ul></nav>
      <nav aria-label="Lavora con noi"><h3>Lavora con noi</h3><ul><li><a href="/#demo">Prenota una demo</a></li><li><a href="/#inizio">Come si parte</a></li><li><a href="/pricing">Listino</a></li>{'<li><a href="/reti">Reti di partner</a></li>' if SHOW_RETI else ''}</ul></nav>
      <nav aria-label="Note legali"><h3>Note legali</h3><ul>{legal_nav}</ul></nav>
    </div>
    <div class="foot-bottom"><span>{foot_bottom()}</span><a class="to-top" href="#top">Torna su <span aria-hidden="true">↑</span></a></div>
  </div>
</footer>
<script>
const menuBtn=document.getElementById('menuBtn'),sheet=document.getElementById('sheet');
function setMenu(o){{menuBtn.setAttribute('aria-expanded',o);menuBtn.setAttribute('aria-label',o?'Chiudi il menu':'Apri il menu');sheet.hidden=!o;document.body.style.overflow=o?'hidden':'';}}
menuBtn.addEventListener('click',()=>setMenu(menuBtn.getAttribute('aria-expanded')!=='true'));
sheet.addEventListener('click',e=>{{if(e.target.closest('a'))setMenu(false);}});
addEventListener('keydown',e=>{{if(e.key==='Escape'&&!sheet.hidden){{setMenu(false);menuBtn.focus();}}}});
</script>
</body>
</html>
'''


def flow_svg(colors=None):
    """Immagine di riferimento Human Flow: i nastri entrano nell'ottagono. Decorativa (alt vuoto)."""
    return ('<div class="sv-art" aria-hidden="true"><img src="/img/ribbons-1200.webp" alt="" width="1200" height="675" '
            'decoding="async" fetchpriority="high"></div>')


def loop_steps(s):
    if s["ok"]:
        steps = [("Il sistema prepara", "Gli agenti preparano il lavoro sui canali che usi già."),
                 ("Le regole lo controllano", "Limiti scritti nel codice fermano ciò che esce dai margini."),
                 ("Tu dai l'ok", "Su Telegram: approvi o rifiuti. Senza ok, nulla parte."),
                 ("Esegue e registra", "Quello che approvi esce, e resta traccia di ogni scelta.")]
        gate = 2
    else:
        steps = [("Il sistema raccoglie", "Dati letti con regolarità dai canali e dal mercato."),
                 ("Ordina e confronta", "Concorrenti, prezzi e risultati messi in fila."),
                 ("Ti arriva il report", "Ogni lunedì, chiaro, senza cruscotti da interpretare."),
                 ("Decidi tu", "Le proposte che ne nascono passano dal controllo.")]
        gate = 3
    return "".join(f'<li{" class=\"gate\"" if i == gate else ""}><b>{t}</b>{d}</li>' for i, (t, d) in enumerate(steps))


def areas_nav(current_slug=None):
    out = []
    for key, name, col in AREAS:
        items = "".join(
            f'<li><a href="/servizi/{s["slug"]}"{" aria-current=\"page\"" if s["slug"] == current_slug else ""}>{E(s["name"])}</a></li>'
            for s in services_in(key))
        out.append(f'<section style="--a:{col}"><h3>{name}</h3><ul>{items}</ul></section>')
    return f'<div class="sv-areas">{"".join(out)}</div>'


def org_ld():
    return {"@type": "Organization", "@id": SITE + "/#org", "name": "Octagon", "url": SITE + "/",
            "logo": SITE + "/logo.png", "email": EMAIL}


def service_page(s):
    key, aname, acol = area(s["area"])
    path = "/servizi/" + s["slug"]
    plan = quote(s["name"])
    ok_tag = (f'<p class="sv-tag"><i></i>Serve il tuo ok: {E(s["you"][0].lower() + s["you"][1:])}</p>' if s["ok"]
              else '<p class="sv-tag read"><i></i>Solo lettura: il sistema non esegue azioni</p>')
    third = (f'<li class="sv-card"><span class="n">03 · Cosa sostituisce</span><h2>Al posto di</h2><p>{E(s["replaces"])}</p></li>'
             if s["replaces"] else
             f'<li class="sv-card"><span class="n">03 · Dove esce</span><h2>Collegato a</h2><ul class="chips">{"".join(f"<li>{E(w)}</li>" for w in s["where"])}</ul></li>')
    colors = (s["color"] if not s.get("dark") else "#5FB3A8", acol if not s.get("dark") else "#8C7CE0", "#F0B08A")
    main = f'''<header class="sv-head" style="--c:{acol}">
  <div class="wrap">
    <ol class="crumbs" aria-label="Percorso"><li><a href="/">Home</a></li><li><a href="/#aree">Cosa fa</a></li><li>{aname}</li></ol>
    <p class="eyebrow"><i aria-hidden="true" style="background:{acol}"></i>Servizio · {aname}</p>
    <h1>{E(s["name"])}</h1>
    <p class="lede">{E(s["desc"])}</p>
    {ok_tag}
    <div class="ctas"><a class="btn btn-primary" href="/?piano={plan}#demo">Parliamone <span class="arr" aria-hidden="true">→</span></a><a class="btn btn-ghost" href="/pricing">Vedi il listino</a></div>
  </div>
  {flow_svg(colors)}
</header>
<div class="wrap sv-body">
  <ul class="sv-grid" style="--c:{s["color"]}">
    <li class="sv-card"><span class="n">01 · Cosa fa</span><h2>Il lavoro che prende in carico</h2><p>{E(s["what"])}</p></li>
    <li class="sv-card{" ok" if s["ok"] else ""}"><span class="n">02 · Dove serve il tuo ok</span><h2>{"Decidi tu" if s["ok"] else "Nessuna azione"}</h2><p>{E(s["you"])}</p></li>
    {third}
  </ul>
  <section class="sv-loop" aria-labelledby="loop-h">
    <h2 id="loop-h">Come lavora<span class="s">con te.</span></h2>
    <ol class="steps4">{loop_steps(s)}</ol>
  </section>
  <section class="sv-more" aria-labelledby="more-h">
    <h2 id="more-h">Dieci servizi, un solo sistema.</h2>
    {areas_nav(s["slug"])}
  </section>
  <section class="sv-cta" aria-labelledby="cta-h">
    <div><h2 id="cta-h">{E(s["name"])}: <span class="s">da dove si comincia?</span></h2><p>Una call di 20 minuti. Ti diciamo cosa prende in carico il sistema, e cosa no.</p></div>
    <div class="ctas"><a class="btn btn-primary" href="/?piano={plan}#demo">Prenota una demo <span class="arr" aria-hidden="true">→</span></a></div>
  </section>
</div>'''
    ld = [{"@context": "https://schema.org", "@graph": [
        org_ld(),
        {"@type": "Service", "@id": SITE + path + "#service", "name": s["name"], "description": s["desc"], "url": SITE + path,
         "provider": {"@id": SITE + "/#org"}, "serviceType": s["name"], "category": aname,
         "areaServed": [{"@type": "Country", "name": n} for n in AREA_SERVED]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Cosa fa", "item": SITE + "/#aree"},
            {"@type": "ListItem", "position": 3, "name": s["name"], "item": SITE + path}]}]}]
    return chrome(path, s["title"], s["desc"], main, ld)


def reti_page():
    plan = quote(RETI["plan"])
    parts = [("Schede e listini", "Allineati in ogni punto vendita, con le regole della casa madre."),
             ("Contenuti nel marchio", "Ogni partner pubblica con l'identità della casa madre."),
             ("Campagne locali", "Dentro un budget approvato.")]
    cards = "".join(f'<li class="sv-card"><span class="n">0{i} · Per ogni partner</span><h2>{t}</h2><p>{d}</p></li>' for i, (t, d) in enumerate(parts, 1))
    main = f'''<header class="sv-head" style="--c:#8C7CE0">
  <div class="wrap">
    <ol class="crumbs" aria-label="Percorso"><li><a href="/">Home</a></li><li>Reti di partner</li></ol>
    <p class="eyebrow"><i aria-hidden="true" style="background:#8C7CE0"></i>Reti di partner</p>
    <h1>{E(RETI["h1"])}<span class="s">{E(RETI["h1s"])}</span></h1>
    <p class="lede">{E(RETI["text"])}</p>
    <div class="ctas"><a class="btn btn-primary" href="/?piano={plan}#demo">{RETI["cta"]} <span class="arr" aria-hidden="true">→</span></a><a class="btn btn-ghost" href="/pricing">Vedi il listino</a></div>
  </div>
  {flow_svg(("#5FB3A8", "#8C7CE0", "#F0B08A"))}
</header>
<div class="wrap sv-body">
  <ul class="rt-grid">{cards}</ul>
  <section class="sv-loop" aria-labelledby="loop-h">
    <h2 id="loop-h">Come si parte<span class="s">con la rete.</span></h2>
    <ol class="steps4">
      <li><b>Le regole della casa madre</b>Marchio, listini e limiti di spesa, fissati una volta.</li>
      <li><b>Un pilota</b>Da 3 a 5 partner, per 90 giorni.</li>
      <li class="gate"><b>L'ok resta umano</b>Le azioni che contano aspettano un'approvazione.</li>
      <li><b>Lo stesso sistema</b>Gli stessi servizi, in ogni punto vendita.</li>
    </ol>
  </section>
  <section class="sv-more" aria-labelledby="more-h">
    <h2 id="more-h">I servizi che riceve ogni partner.</h2>
    {areas_nav()}
  </section>
  <section class="sv-cta" aria-labelledby="cta-h">
    <div><h2 id="cta-h">Una rete da allineare? <span class="s">Parliamone.</span></h2><p>Prezzo per sede su richiesta.</p></div>
    <div class="ctas"><a class="btn btn-primary" href="/?piano={plan}#demo">{RETI["cta"]} <span class="arr" aria-hidden="true">→</span></a></div>
  </section>
</div>'''
    ld = [{"@context": "https://schema.org", "@graph": [org_ld(),
        {"@type": "Service", "name": "Reti di partner", "description": RETI["desc"], "url": SITE + "/reti",
         "provider": {"@id": SITE + "/#org"}, "areaServed": [{"@type": "Country", "name": n} for n in AREA_SERVED]}]}]
    return chrome("/reti", RETI["title"], RETI["desc"], main, ld)


def board_html():
    """Le dieci schede della sezione «Cosa fa»: HTML statico, il JS aggiunge solo l'apertura."""
    out = []
    for i, s in enumerate(SERVICES):
        _, aname, _ = area(s["area"])
        n = f"{i + 1:02d}"
        third = (f'<div><b>Cosa sostituisce</b>{E(s["replaces"])}</div>' if s["replaces"]
                 else f'<div><b>Collegato a</b>{E(", ".join(s["where"]))}</div>')
        out.append(
            f'<div class="lane{" open" if i == 0 else ""}{" dark" if s.get("dark") else ""}" style="--c:{s["color"]}">'
            f'<button class="lane-tab" type="button" id="lt{i}" aria-expanded="{"true" if i == 0 else "false"}" aria-controls="lb{i}">'
            f'<span class="ribbon" aria-hidden="true"></span><span class="lane-n">{n}</span>'
            f'{"<span class=\"lane-ok\" aria-hidden=\"true\"></span>" if s["ok"] else ""}<span class="lane-t">{E(s["short"])}</span></button>'
            f'<div class="lane-body" id="lb{i}" role="region" aria-labelledby="lt{i}">'
            f'<span class="k">{aname} · {n}</span><h3>{E(s["name"])}</h3><p>{E(s["what"])}</p>'
            f'<div class="lane-meta"><div class="{"okbox" if s["ok"] else ""}"><b>{"Serve il tuo ok" if s["ok"] else "Il tuo ok"}</b>{E(s["you"])}</div>{third}</div>'
            f'<a class="lane-link" href="/servizi/{s["slug"]}">Apri il servizio <span aria-hidden="true">→</span></a>'
            f'</div></div>')
    return "".join(out)


def home_jsonld():
    faq = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in HOME_FAQ]
    g = {"@context": "https://schema.org", "@graph": [
        dict(org_ld(), description="Octagon è uno studio founder-led che costruisce e gestisce sistemi di agenti AI per il lavoro operativo di aziende e brand. Ogni azione che conta passa da un'approvazione umana su Telegram."),
        {"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": "Octagon", "inLanguage": "it-IT", "publisher": {"@id": SITE + "/#org"}},
        {"@type": "FAQPage", "mainEntity": faq}]}
    return f'<script type="application/ld+json">{json.dumps(g, ensure_ascii=False)}</script>'


def wa_url():
    return f"https://wa.me/{WHATSAPP}?text={quote(WHATSAPP_TEXT)}"


WA_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
           '<path d="M21 11.5a8.5 8.5 0 0 1-12.4 7.6L3.5 20.5l1.4-4.8A8.5 8.5 0 1 1 21 11.5z"/>'
           '<circle cx="8.6" cy="11.5" r=".6" fill="currentColor"/><circle cx="12.4" cy="11.5" r=".6" fill="currentColor"/><circle cx="16.2" cy="11.5" r=".6" fill="currentColor"/></svg>')


def wa_fab():
    return (f'<a class="wa-fab" href="{wa_url()}" target="_blank" rel="noopener" '
            f'aria-label="Scrivici su WhatsApp (si apre in una nuova finestra)">{WA_ICON}<span>Scrivici su WhatsApp</span></a>')


def add_wa(text):
    """Foglio di stile in testa e pulsante prima di </body>, tra marcatori (idempotente)."""
    if "<!-- @wa-css -->" not in text:
        text = text.replace("</head>", '<link rel="stylesheet" href="/wa.css"><!-- @wa-css -->\n</head>', 1)
    if "<!-- @wa:start -->" not in text:
        text = text.replace("</body>", "<!-- @wa:start --><!-- @wa:end -->\n</body>", 1)
    return splice(text, "<!-- @wa:start -->", "<!-- @wa:end -->", wa_fab())


def splice(text, start, end, inner):
    a, b = text.index(start) + len(start), text.index(end)
    return text[:a] + inner + text[b:]


def llms_txt():
    lines = ["# Octagon", "",
             "> Octagon è uno studio founder-led che costruisce e gestisce sistemi di agenti AI per il lavoro operativo di aziende e brand, "
             "dal negozio indipendente al marchio internazionale con distributori e punti vendita. Il sistema prepara il lavoro; "
             "ogni azione che conta parte solo dopo l'approvazione di una persona su Telegram.", "",
             "Il sistema usa 46 workflow (38 attivi ogni giorno) e 8 agenti AI su infrastruttura gestita da Octagon. "
             "Regole scritte nel codice, come un prezzo minimo o un limite di spesa, fermano le proposte fuori dai margini prima che arrivino alla persona.", "",
             "## Servizi", ""]
    for key, name, _ in AREAS:
        lines.append(f"### {name}")
        for s in services_in(key):
            r = f" Sostituisce: {s['replaces'][0].lower() + s['replaces'][1:]}" if s["replaces"] else ""
            ok = f"Approvazione richiesta: {s['you'][0].lower() + s['you'][1:]}" if s["ok"] else "Solo lettura: nessuna azione eseguita."
            lines.append(f"- [{s['name']}]({SITE}/servizi/{s['slug']}): {s['what']} {ok}{r}")
        lines.append("")
    if SHOW_RETI:
        lines += ["## Reti di partner", "", f"- [Reti di partner]({SITE}/reti): {RETI['text']}", ""]
    lines += ["## Listino", "",
              f"- [Listino]({SITE}/pricing): pacchetti Starter (€599 di avvio, poi €99 al mese, 5 workflow attivi), Growth (€1.500, poi €299 al mese, 15 workflow), "
              "Scale (€2.499, poi €499 al mese, 24 workflow), Enterprise (da €3.999, canone su misura, 38 workflow). Prezzi IVA esclusa. "
              "Aggiunte mensili componibili; siti e negozi a progetto: landing page €799, negozio Shopify €1.500, applicazione su misura su preventivo.", "",
              "## Contatti", "", f"- Email: {EMAIL}", f"- Richiesta demo: {SITE}/#demo", "",
              "## Note", "", f"- [Privacy]({SITE}/privacy)", f"- [Termini di servizio]({SITE}/termini)", ""]
    return "\n".join(lines)


def sitemap():
    paths = ["/", "/pricing"] + [f"/servizi/{s['slug']}" for s in SERVICES] + (["/reti"] if SHOW_RETI else []) + ["/privacy", "/cookie", "/termini"]
    urls = "".join(f"<url><loc>{SITE}{'' if p == '/' else p}{'/' if p == '/' else ''}</loc></url>" for p in paths)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'


def update_nav(text):
    """Aggiunge o toglie il link Reti di partner accanto a Listino (menu e foglio mobile) nelle pagine esistenti."""
    text = re.sub(r'\n[ \t]*<a( class="l")? href="/reti">Reti di partner</a>', "", text)
    if SHOW_RETI:
        text = re.sub(r'(\n([ \t]*)<a( class="l")? href="/pricing"( aria-current="page")?>Listino</a>)',
                      lambda m: m.group(1) + "\n" + m.group(2) + f'<a{m.group(3) or ""} href="/reti">Reti di partner</a>', text)
    return text


def pricing_jsonld():
    """Solo i prezzi pubblicati (documento, sezione SEO). Le voci «Su preventivo» restano fuori."""
    def offer(name, price, desc, unit=None):
        o = {"@type": "Offer", "name": name, "description": desc, "priceCurrency": "EUR", "price": price,
             "valueAddedTaxIncluded": False, "seller": {"@id": SITE + "/#org"}}
        if unit:
            o["priceSpecification"] = {"@type": "UnitPriceSpecification", "price": price, "priceCurrency": "EUR", "unitText": unit}
        return o
    cat = {"@type": "OfferCatalog", "name": "Listino OCTAGON", "url": SITE + "/pricing", "itemListElement": [
        {"@type": "OfferCatalog", "name": "Pacchetti", "itemListElement": [
            offer("Starter · avvio", "599", "Costo di avvio una tantum, 5 workflow attivi"),
            offer("Starter · canone", "99", "Canone mensile", "mese"),
            offer("Growth · avvio", "1500", "Costo di avvio una tantum, 15 workflow attivi"),
            offer("Growth · canone", "299", "Canone mensile", "mese"),
            offer("Scale · avvio", "2499", "Costo di avvio una tantum, 24 workflow attivi"),
            offer("Scale · canone", "499", "Canone mensile", "mese"),
            offer("Enterprise · avvio", "3999", "Da €3.999 di avvio, canone su misura, 38 workflow attivi")]},
        {"@type": "OfferCatalog", "name": "Aggiunte", "itemListElement": [
            offer("Contenuti AI", "99", "Testi, immagini e video per i canali, consegnati in bozza", "mese"),
            offer("Foto e video in sede", "79", "Foto prodotto, scene e video brevi creati in sede", "mese"),
            offer("Analisi e report", "59", "Riepilogo giornaliero e report settimanale", "mese")]},
        {"@type": "OfferCatalog", "name": "Siti e negozi", "itemListElement": [
            offer("Landing page", "799", "Una pagina costruita per un solo obiettivo"),
            offer("Negozio Shopify", "1500", "Il negozio completo, da zero fino a online")]}]}
    g = {"@context": "https://schema.org", "@graph": [org_ld(), cat]}
    return f'<script type="application/ld+json">{json.dumps(g, ensure_ascii=False)}</script>'



if __name__ == "__main__":
    (ROOT / "servizi").mkdir(exist_ok=True)
    for s in SERVICES:
        (ROOT / "servizi" / f"{s['slug']}.html").write_text(add_wa(service_page(s)))
    reti = ROOT / "reti.html"
    if SHOW_RETI:
        reti.write_text(add_wa(reti_page()))
    elif reti.exists():
        reti.unlink()

    idx = ROOT / "index.html"
    t = idx.read_text()
    t = splice(t, "<!-- @services:start -->", "<!-- @services:end -->", board_html())
    t = splice(t, "<!-- @jsonld:start -->", "<!-- @jsonld:end -->", home_jsonld())
    t = update_nav(t)
    t = add_wa(t)
    t = re.sub(r'<a class="wa-inline"[^>]*href="[^"]*"', lambda m: re.sub(r'href="[^"]*"', f'href="{wa_url()}"', m.group(0)), t)
    idx.write_text(t)

    pr = ROOT / "pricing.html"
    t = pr.read_text()
    t = splice(t, "<!-- @jsonld:start -->", "<!-- @jsonld:end -->", pricing_jsonld())
    t = update_nav(t)
    t = add_wa(t)
    t = re.sub(r'<div data-reti-row.*?</a></div></div>', lambda m: m.group(0) if SHOW_RETI else "", t, flags=re.S)
    pr.write_text(t)

    for name in ("privacy.html", "cookie.html", "termini.html"):
        f = ROOT / name
        f.write_text(add_wa(update_nav(f.read_text())))

    (ROOT / "llms.txt").write_text(llms_txt())
    (ROOT / "sitemap.xml").write_text(sitemap())
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    print("Generate:", len(SERVICES), "pagine servizio", "+ reti" if SHOW_RETI else "(reti spenta)", "+ llms.txt, sitemap.xml, robots.txt")
