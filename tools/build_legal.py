#!/usr/bin/env python3
"""Genera privacy.html, cookie.html e termini.html con la stessa navigazione e lo stesso piede del sito.

Uso:  python3 tools/build_legal.py
I dati societari si compilano nel dizionario DATI qui sotto: un valore None viene mostrato
come campo "da completare" (evidenziato), così nessun dato viene inventato.
"""
from pathlib import Path
import html, re

ROOT = Path(__file__).resolve().parent.parent
AGGIORNATO = "1 ottobre 2026"
AGGIORNATO_ISO = "2026-10-01"

DATI = {
    "titolare": "Edison Zoicaj",        # es. "Mario Rossi, titolare della ditta individuale Octagon" o "Octagon S.r.l."
    "piva": None,            # partita IVA
    "cf": None,              # codice fiscale (se diverso dalla P.IVA)
    "sede": None,            # indirizzo completo
    "email": "info@theoctagonai.com",           # email per privacy e contatti
    "pec": None,             # facoltativa: lasciare None per non mostrarla
    "foro": None,            # es. "Bologna"
    "iva_listino": "IVA esclusa",     # es. "IVA esclusa"
}
FACOLTATIVI = {"pec", "cf", "piva", "sede", "foro"}  # se assenti, le righe vengono omesse

ETICHETTE = {
    "titolare": "nome e cognome o ragione sociale", "piva": "partita IVA", "cf": "codice fiscale",
    "sede": "indirizzo della sede", "email": "email di contatto", "pec": "PEC", "foro": "città del foro",
    "iva_listino": "regime IVA dei prezzi",
}


def d(k):
    v = DATI.get(k)
    if v:
        if k in ("email", "pec"):
            return f'<a class="dato" href="mailto:{html.escape(v)}">{html.escape(v)}</a>'
        return f'<span class="dato">{html.escape(v)}</span>'
    return f'<span class="dato todo">da completare: {ETICHETTE[k]}</span>'


def foro_frase():
    if DATI["foro"]:
        return f'Per le controversie tra imprese è competente in via esclusiva il foro di {d("foro")}.'
    return "Per le controversie tra imprese è competente il foro del luogo in cui ha sede il titolare."


def mancanti():
    return [k for k, v in DATI.items() if not v and k not in FACOLTATIVI]


LOGO = ('<svg viewBox="0 0 100 100" aria-hidden="true"><polygon points="29.3,0 70.7,0 100,29.3 100,70.7 70.7,100 29.3,100 0,70.7 0,29.3" fill="#1F7A74"/>'
        '<polygon points="29.3,0 70.7,0 100,29.3 50,50" fill="#D9D2C8"/><polygon points="100,70.7 70.7,100 50,50 100,29.3" fill="#E0613A"/>'
        '<polygon points="29.3,100 0,70.7 50,50 70.7,100" fill="#8C7CE0"/><polygon points="36,26 64,26 74,36 74,64 64,74 36,74 26,64 26,36" fill="#F4EFE8"/></svg>')

OCT_DECOR = ('<svg class="lg-oct" viewBox="0 0 100 100" aria-hidden="true"><defs><linearGradient id="og" x1="0" y1="0" x2="1" y2="1">'
             '<stop offset="0" stop-color="#DDEFEB"/><stop offset=".55" stop-color="#ECE8FB"/><stop offset="1" stop-color="#FBE3D8"/></linearGradient></defs>'
             '<polygon points="29.3,0 70.7,0 100,29.3 100,70.7 70.7,100 29.3,100 0,70.7 0,29.3" fill="url(#og)"/>'
             '<polygon points="36,26 64,26 74,36 74,64 64,74 36,74 26,64 26,36" fill="none" stroke="#1F7A74" stroke-width=".8" opacity=".5"/></svg>')

PAGINE = [("/privacy", "Privacy"), ("/cookie", "Cookie"), ("/termini", "Termini di servizio")]


def foot_bottom():
    parti = ["© 2026 Octagon"]
    if DATI["titolare"]:
        parti.append(html.escape(DATI["titolare"]))
    if DATI["piva"]:
        parti.append("P.IVA " + html.escape(DATI["piva"]))
    return " · ".join(parti) + ". Tutti i diritti riservati."


def page(path, title, description, eyebrow, h1, lede, brief, sections):
    toc = "".join(f'<li><a href="#{sid}">{html.escape(t)}</a></li>' for sid, t, _ in sections)
    others = "".join(f'<a href="{p}">{n}</a>' for p, n in PAGINE if p != path)
    cur = ' aria-current="page"'
    legal_nav = "".join(f'<li><a href="{p}"{cur if p == path else ""}>{n}</a></li>' for p, n in PAGINE)
    body = "".join(
        f'<section id="{sid}" aria-labelledby="{sid}-h"><span class="num">{i:02d}</span><h2 id="{sid}-h">{html.escape(t)}</h2>{content}</section>'
        for i, (sid, t, content) in enumerate(sections, 1))
    brief_html = "".join(f"<li><span>{b}</span></li>" for b in brief)
    url = "https://theoctagonai.com" + path
    return f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(title)} · Octagon</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Octagon"><meta property="og:url" content="{url}">
<meta property="og:title" content="{html.escape(title)} · Octagon"><meta property="og:description" content="{html.escape(description)}"><meta property="og:image" content="https://theoctagonai.com/og.jpg">
<meta name="theme-color" content="#F4EFE8">
<style>[hidden]{{display:none!important}}body{{margin:0}}</style>
<link rel="preload" href="/fonts/public-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/bricolage-grotesque-opsz.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/fonts/fonts.css">
<link rel="stylesheet" href="/legal.css">
</head>
<body id="top">
<a class="skip" href="#contenuto">Vai al contenuto</a>
<header class="nav" id="nav">
  <div class="wrap nav-in">
    <a class="logo" href="/#top" aria-label="Octagon, vai alla home">{LOGO}octagon</a>
    <nav class="links" aria-label="Principale">
      <a href="/#settimana">La tua settimana</a>
      <a href="/#ciclo">Come funziona</a>
      <a href="/#cancello">Il controllo</a>
      <a href="/#aree">Cosa fa</a>
      <a href="/#sistema">Tecnologia</a>
      <a href="/pricing">Listino</a>
      <a href="/reti">Reti di partner</a>
    </nav>
    <a class="btn btn-dark nav-cta" href="/#demo">Prenota una demo <span class="arr" aria-hidden="true">→</span></a>
    <button class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="sheet" aria-label="Apri il menu"><span></span></button>
  </div>
</header>
<div class="sheet" id="sheet" hidden>
  <a class="l" href="/#settimana">La tua settimana</a>
  <a class="l" href="/#ciclo">Come funziona</a>
  <a class="l" href="/#cancello">Il controllo</a>
  <a class="l" href="/#aree">Cosa fa</a>
  <a class="l" href="/#sistema">Tecnologia</a>
  <a class="l" href="/pricing">Listino</a>
  <a class="l" href="/reti">Reti di partner</a>
  <a class="btn btn-primary" href="/#demo">Prenota una demo <span class="arr" aria-hidden="true">→</span></a>
</div>

<main class="legal" id="contenuto">
  <header class="lg-head">
    <div class="wrap">
      <p class="eyebrow"><i aria-hidden="true"></i>{eyebrow}</p>
      <h1>{h1}</h1>
      <p class="lede">{lede}</p>
      <p class="lg-meta"><span>Ultimo aggiornamento <b><time datetime="{AGGIORNATO_ISO}">{AGGIORNATO}</time></b></span><span>Titolare <b>{d("titolare")}</b></span></p>
    </div>
    {OCT_DECOR}
  </header>
  <div class="wrap lg-body">
    <nav class="toc" aria-label="Indice della pagina">
      <h2>In questa pagina</h2>
      <ol>{toc}</ol>
      <div class="other" aria-label="Altre note legali">{others}</div>
    </nav>
    <article class="doc">
      <div class="brief"><h2>In <em class="s">breve</em></h2><ul>{brief_html}</ul></div>
      {body}
      <div class="lg-cta"><div><strong>Una domanda su questa pagina?</strong><p>Scrivici: rispondiamo noi, una persona, non un modulo automatico.</p></div>{contact_button()}</div>
    </article>
  </div>
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
      <nav aria-label="Il percorso"><h3>Il percorso</h3><ul><li><a href="/#settimana">La tua settimana</a></li><li><a href="/#ciclo">Come funziona</a></li><li><a href="/#cancello">Il controllo umano</a></li><li><a href="/#aree">Cosa fa</a></li><li><a href="/#sistema">Tecnologia</a></li></ul></nav>
      <nav aria-label="Lavora con noi"><h3>Lavora con noi</h3><ul><li><a href="/#demo">Prenota una demo</a></li><li><a href="/#inizio">Come si parte</a></li><li><a href="/pricing">Listino</a></li></ul></nav>
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
// indice: evidenzia la sezione in lettura
const links=[...document.querySelectorAll('.toc ol a')];
const io=new IntersectionObserver(es=>{{es.forEach(e=>{{if(e.isIntersecting){{links.forEach(a=>a.classList.toggle('on',a.hash==='#'+e.target.id));}}}});}},{{rootMargin:'-30% 0px -60% 0px'}});
document.querySelectorAll('.doc section').forEach(s=>io.observe(s));
</script>
</body>
</html>
'''


def contact_button():
    if DATI["email"]:
        e = html.escape(DATI["email"])
        return f'<a class="btn btn-ghost" href="mailto:{e}">Scrivi a {e}</a>'
    return '<a class="btn btn-ghost" href="/#demo">Contattaci <span class="arr" aria-hidden="true">→</span></a>'


# ---------------------------------------------------------------- PRIVACY
def privacy():
    pec = f'<dt>PEC</dt><dd>{d("pec")}</dd>' if DATI["pec"] else ""
    cf = f'<dt>Codice fiscale</dt><dd>{d("cf")}</dd>' if DATI["cf"] else ""
    piva = f'<dt>Partita IVA</dt><dd>{d("piva")}</dd>' if DATI["piva"] else ""
    sede = f'<dt>Sede</dt><dd>{d("sede")}</dd>' if DATI["sede"] else ""
    s = [
        ("titolare", "Chi tratta i tuoi dati", f'''
<p>Il titolare del trattamento è chi decide perché e come vengono usati i tuoi dati personali. Per questo sito e per i servizi di Octagon è:</p>
<dl><dt>Titolare</dt><dd>{d("titolare")}</dd>{piva}{cf}{sede}<dt>Email</dt><dd>{d("email")}</dd>{pec}</dl>
<p>Octagon è uno studio di piccole dimensioni e non è tenuto a nominare un responsabile della protezione dei dati (DPO). Per qualsiasi richiesta sui tuoi dati scrivi all'indirizzo email qui sopra: ti risponde direttamente il titolare.</p>'''),
        ("dati", "Quali dati raccogliamo", '''
<h3>Quando visiti il sito</h3>
<p>Il server che ospita il sito registra in automatico alcuni dati tecnici di ogni richiesta: indirizzo IP, data e ora, pagina richiesta, tipo di browser e di dispositivo, eventuali errori. Servono a far funzionare il sito e a proteggerlo da abusi. Non li usiamo per profilarti e non li incrociamo con altri dati.</p>
<p>Il sito <strong>non usa cookie</strong>, non usa strumenti di statistica o pubblicità e non carica risorse da servizi di terze parti: anche i caratteri tipografici sono ospitati sul nostro dominio. I dettagli sono nella <a href="/cookie">cookie policy</a>.</p>
<h3>Quando chiedi una demo</h3>
<p>Con il modulo “Prenota una demo” ci invii il tuo <strong>nome</strong> e la tua <strong>email di lavoro</strong>, che sono obbligatori, e se vuoi il nome della tua <strong>attività</strong> e una descrizione del <strong>lavoro che si ripete</strong>. Ti chiediamo di non inserire nella descrizione dati personali di altre persone né dati particolari (salute, opinioni politiche o religiose e simili): per capire il tuo caso non servono.</p>
<h3>Quando ci scrivi o diventi cliente</h3>
<p>Se ci contatti via email o Telegram trattiamo i dati che ci comunichi e quelli necessari per risponderti. Se diventi cliente trattiamo anche i dati per la fatturazione e la gestione del contratto (nome o ragione sociale, partita IVA, indirizzo, recapiti di chi lavora con noi).</p>'''),
        ("finalita", "Perché li usiamo e su quale base", '''
<div class="tbl"><table>
<thead><tr><th scope="col">Finalità</th><th scope="col">Dati</th><th scope="col">Base giuridica (GDPR)</th></tr></thead>
<tbody>
<tr><td>Far funzionare il sito e proteggerlo</td><td>Dati tecnici di navigazione</td><td>Legittimo interesse alla sicurezza e al funzionamento del sito (art. 6.1.f)</td></tr>
<tr><td>Rispondere alla richiesta di demo e preparare una proposta</td><td>Dati del modulo e della corrispondenza</td><td>Misure precontrattuali richieste da te (art. 6.1.b)</td></tr>
<tr><td>Erogare i servizi e gestire il rapporto</td><td>Dati di contatto e di fatturazione</td><td>Esecuzione del contratto (art. 6.1.b)</td></tr>
<tr><td>Adempiere agli obblighi fiscali e contabili</td><td>Dati di fatturazione</td><td>Obbligo di legge (art. 6.1.c)</td></tr>
<tr><td>Difendere i nostri diritti in caso di contestazioni</td><td>Dati necessari al caso</td><td>Legittimo interesse (art. 6.1.f)</td></tr>
</tbody></table></div>
<p>Non usiamo i tuoi dati per inviarti newsletter o pubblicità, non li vendiamo e non li cediamo a terzi per i loro scopi. Se un giorno volessimo farlo, ti chiederemmo prima un consenso separato e facoltativo.</p>
<p>Non prendiamo decisioni basate unicamente su trattamenti automatizzati che producano effetti giuridici su di te o che ti riguardino in modo analogo (art. 22 GDPR): ogni richiesta viene letta e valutata da una persona.</p>'''),
        ("obbligo", "Sei obbligato a darci i tuoi dati?", '''
<p>No. Per navigare il sito non devi fornire nulla. Nome ed email sono necessari solo se vuoi che rispondiamo alla tua richiesta di demo: senza di essi non possiamo ricontattarti. Gli altri campi del modulo sono facoltativi.</p>'''),
        ("destinatari", "Chi altro vede i dati", '''
<p>I dati sono trattati da Octagon. Per alcune attività ci appoggiamo a fornitori che li trattano per nostro conto, solo per il servizio richiesto e in base a un accordo sul trattamento dei dati (art. 28 GDPR):</p>
<ul>
<li><strong>Vercel Inc.</strong> (Stati Uniti): ospita il sito e registra i dati tecnici di navigazione.</li>
<li><strong>Resend</strong> (Plus Five Five, Inc., Stati Uniti): inoltra a Octagon via email le richieste inviate con il modulo demo.</li>
<li>Il fornitore della nostra <strong>casella di posta</strong>, dove ricevi e conserviamo la corrispondenza.</li>
<li><strong>Telegram</strong>, solo se scegli di scriverci lì: in quel caso si applica anche l'informativa privacy di Telegram.</li>
<li>Il nostro <strong>commercialista</strong>, per i soli dati di fatturazione dei clienti.</li>
</ul>
<p>Possiamo comunicare i dati alle autorità solo quando la legge lo impone.</p>'''),
        ("estero", "Trasferimenti fuori dall'Unione europea", '''
<p>Vercel e Resend hanno sede negli Stati Uniti. Entrambe sono certificate nell'ambito dell'<strong>EU-U.S. Data Privacy Framework</strong>, riconosciuto adeguato dalla Commissione europea con la decisione del 10 luglio 2023 (art. 45 GDPR). Puoi verificare la certificazione sul sito ufficiale <a href="https://www.dataprivacyframework.gov/list" rel="noopener">dataprivacyframework.gov</a>.</p>'''),
        ("conservazione", "Per quanto tempo li conserviamo", '''
<ul>
<li><strong>Dati tecnici di navigazione</strong>: per il periodo limitato previsto dai registri del fornitore di hosting, poi cancellati in automatico.</li>
<li><strong>Richieste di demo e corrispondenza</strong> che non portano a un contratto: 12 mesi dall'ultimo contatto, poi cancellate.</li>
<li><strong>Dati contrattuali e di fatturazione</strong>: 10 anni dalla chiusura dell'esercizio, come richiesto dalla legge (art. 2220 del Codice civile).</li>
</ul>
<p>Se ci chiedi di cancellare i tuoi dati prima di queste scadenze lo facciamo, salvo quelli che la legge ci obbliga a conservare.</p>'''),
        ("clienti", "I dati che trattiamo per conto dei clienti", '''
<p>Quando i sistemi di Octagon lavorano per un cliente (per esempio rispondono ai suoi clienti, aggiornano annunci o preparano email) possono trattare dati personali di persone terze. Per quei dati il titolare è il cliente e Octagon agisce come <strong>responsabile del trattamento</strong> (art. 28 GDPR), secondo un accordo scritto che indica dati, finalità, misure di sicurezza e fornitori coinvolti.</p>
<p>Le azioni che contano passano dall'approvazione di una persona prima di essere eseguite, e i controlli su prezzi, limiti di spesa e regole sono scritti nel codice.</p>'''),
        ("diritti", "I tuoi diritti", f'''
<p>In qualsiasi momento puoi chiederci di:</p>
<ul>
<li>sapere se trattiamo tuoi dati e riceverne una copia (accesso, art. 15);</li>
<li>correggerli o completarli (rettifica, art. 16);</li>
<li>cancellarli (art. 17) o limitarne l'uso (art. 18);</li>
<li>riceverli in un formato leggibile da un computer o farli trasmettere a un altro titolare (portabilità, art. 20);</li>
<li>opporti al trattamento basato sul nostro legittimo interesse (opposizione, art. 21).</li>
</ul>
<p>Scrivi a {d("email")}. Rispondiamo senza costi entro un mese, come previsto dal GDPR. Per proteggere i tuoi dati potremmo chiederti di confermare la tua identità.</p>
<p>Se ritieni che il trattamento violi la normativa puoi proporre reclamo al <a href="https://www.garanteprivacy.it" rel="noopener">Garante per la protezione dei dati personali</a> o all'autorità del Paese dell'UE in cui vivi o lavori.</p>'''),
        ("sicurezza", "Come proteggiamo i dati", '''
<p>Il sito è servito solo in HTTPS. L'accesso ai dati è limitato a chi lavora per Octagon e ne ha bisogno, con credenziali personali e autenticazione a più fattori dove disponibile. Teniamo il minimo indispensabile e cancelliamo ciò che non serve più.</p>'''),
        ("minori", "Minori", '''
<p>Il sito e i servizi sono rivolti a imprese e professionisti. Non raccogliamo consapevolmente dati di minori di 14 anni: se ci accorgiamo di averne ricevuti, li cancelliamo.</p>'''),
        ("modifiche", "Modifiche a questa informativa", f'''
<p>Se cambiamo il modo in cui trattiamo i dati, ad esempio aggiungendo un nuovo fornitore, aggiorniamo questa pagina e la data in alto. Le modifiche importanti le segnaliamo anche sul sito. Versione in vigore dal {AGGIORNATO}.</p>'''),
    ]
    brief = [
        "<strong>Il sito non usa cookie</strong> né strumenti di tracciamento o pubblicità.",
        "Raccogliamo i dati del <strong>modulo demo</strong> solo per risponderti e preparare una proposta.",
        "Non vendiamo i dati e <strong>non li usiamo per marketing</strong> senza un consenso separato.",
        "I fornitori negli Stati Uniti (Vercel, Resend) sono certificati nel <strong>Data Privacy Framework</strong>.",
        "Puoi chiederci in ogni momento di <strong>vedere, correggere o cancellare</strong> i tuoi dati.",
    ]
    return page("/privacy", "Informativa privacy",
                "Come Octagon tratta i dati personali di chi visita il sito, chiede una demo o diventa cliente.",
                "Note legali · Privacy", 'I tuoi dati, <em class="s">spiegati per intero.</em>',
                "Informativa ai sensi degli articoli 13 e 14 del Regolamento (UE) 2016/679 (GDPR) e del Codice privacy (D.Lgs. 196/2003). Scritta per essere letta, non solo firmata.",
                brief, s)


# ---------------------------------------------------------------- COOKIE
def cookie():
    s = [
        ("cosa", "Che cosa sono i cookie", '''
<p>I cookie sono piccoli file di testo che un sito salva nel browser per ricordare informazioni tra una pagina e l'altra o tra una visita e la successiva. Funzionano in modo simile anche altri strumenti, come la memoria locale del browser (<em>localStorage</em>), i pixel di tracciamento e i caratteri o i video caricati da altri siti. In questa pagina li chiamiamo tutti “cookie”.</p>'''),
        ("nostri", "Quali cookie usa questo sito", '''
<p><strong>Nessuno.</strong> theoctagonai.com non installa cookie e non salva informazioni nella memoria del tuo browser: né cookie tecnici, né di statistica, né di profilazione o pubblicità.</p>
<div class="tbl"><table>
<thead><tr><th scope="col">Categoria</th><th scope="col">Usati?</th><th scope="col">Note</th></tr></thead>
<tbody>
<tr><td>Tecnici e di sessione</td><td>No</td><td>Il sito funziona senza ricordare nulla di te.</td></tr>
<tr><td>Statistici (analytics)</td><td>No</td><td>Nessuno strumento di misurazione delle visite.</td></tr>
<tr><td>Profilazione e pubblicità</td><td>No</td><td>Nessun pixel di social network o di piattaforme pubblicitarie.</td></tr>
<tr><td>Contenuti di terze parti</td><td>No</td><td>Caratteri, immagini e codice sono tutti ospitati sul nostro dominio.</td></tr>
</tbody></table></div>
<p class="note">Per questo non vedi un banner dei cookie: secondo le <a href="https://www.garanteprivacy.it/home/docweb/-/docweb-display/docweb/9677876" rel="noopener">Linee guida del Garante del 10 giugno 2021</a>, il consenso serve solo per i cookie non tecnici, e qui non ce ne sono.</p>'''),
        ("terzi", "Servizi di terze parti", '''
<p>Il sito non incorpora video, mappe, pulsanti social o caratteri caricati da altri server. L'unico fornitore coinvolto quando visiti una pagina è <strong>Vercel</strong>, che ospita il sito e registra i dati tecnici di ogni richiesta, come l'indirizzo IP, per farlo funzionare e proteggerlo. Vercel non installa cookie sulle pagine pubbliche di questo sito. I dettagli sono nell'<a href="/privacy">informativa privacy</a>.</p>
<p>Se segui un link verso un altro sito o servizio, come Telegram, valgono le sue regole sui cookie.</p>'''),
        ("verifica", "Come puoi verificarlo", '''
<p>Non devi fidarti sulla parola. Apri gli strumenti per sviluppatori del browser (F12 su computer), vai su <strong>Applicazione</strong> o <strong>Archiviazione</strong> e guarda le voci Cookie e Memoria locale per theoctagonai.com: sono vuote. Nella scheda <strong>Rete</strong> vedrai solo richieste verso il nostro dominio.</p>'''),
        ("gestione", "Come gestire i cookie nel browser", '''
<p>Anche se questo sito non ne usa, puoi bloccare o cancellare i cookie di tutti i siti dalle impostazioni del browser:</p>
<ul>
<li><a href="https://support.google.com/chrome/answer/95647?hl=it" rel="noopener">Google Chrome</a></li>
<li><a href="https://support.apple.com/it-it/guide/safari/sfri11471/mac" rel="noopener">Safari</a></li>
<li><a href="https://support.mozilla.org/it/kb/Eliminare%20i%20cookie" rel="noopener">Mozilla Firefox</a></li>
<li><a href="https://support.microsoft.com/it-it/microsoft-edge/eliminare-i-cookie-in-microsoft-edge-63947406-40ac-c3b8-57b9-2a946a29ae09" rel="noopener">Microsoft Edge</a></li>
</ul>'''),
        ("modifiche", "Se un giorno cambiasse", f'''
<p>Se in futuro aggiungessimo strumenti che usano cookie non tecnici, come statistiche non anonime o pixel pubblicitari, prima aggiorneremo questa pagina e chiederemo il tuo consenso con un banner, lasciandoti la possibilità di rifiutare con la stessa facilità con cui accetti. Versione in vigore dal {AGGIORNATO}.</p>'''),
    ]
    brief = [
        "Questo sito <strong>non usa cookie</strong> né la memoria locale del browser.",
        "<strong>Nessuno strumento</strong> di statistica, pubblicità o social.",
        "Caratteri, immagini e codice sono <strong>ospitati sul nostro dominio</strong>.",
        "Per questo <strong>non serve un banner</strong> per il consenso.",
    ]
    return page("/cookie", "Cookie policy",
                "Il sito di Octagon non usa cookie, strumenti di tracciamento né servizi di terze parti. Ecco come verificarlo.",
                "Note legali · Cookie", 'Nessun cookie. <em class="s">Davvero.</em>',
                "Cookie policy ai sensi dell'art. 122 del Codice privacy e delle Linee guida del Garante del 10 giugno 2021.",
                brief, s)


# ---------------------------------------------------------------- TERMINI
def termini():
    s = [
        ("ambito", "Di cosa parlano questi termini", f'''
<p>Questi termini regolano l'uso del sito theoctagonai.com e, insieme alla proposta commerciale che firmi, i servizi offerti da {d("titolare")} che opera con il marchio Octagon (“Octagon”, “noi”).</p>
<p>I servizi sono rivolti a <strong>imprese e professionisti</strong>. Se agisci come consumatore restano comunque validi tutti i diritti che ti riconosce il Codice del consumo (D.Lgs. 206/2005), e nessuna clausola di questi termini li limita.</p>
<p>Se la proposta firmata e questi termini dicono cose diverse, vale la proposta.</p>'''),
        ("sito", "Le informazioni sul sito", f'''
<p>Descrizioni, esempi e prezzi pubblicati sul sito servono a presentare Octagon. Non sono un'offerta vincolante: il contenuto preciso del servizio, i tempi e il prezzo sono quelli della proposta scritta che ti inviamo. I prezzi del <a href="/pricing">listino</a> sono espressi in euro, {d("iva_listino")}.</p>
<p>Gli esempi di lavoro descritti sul sito (la “settimana”, le richieste su Telegram e simili) illustrano come funziona il sistema e non promettono risultati specifici per la tua attività.</p>'''),
        ("contratto", "Come nasce l'accordo", '''
<p>Di solito si parte da una demo. Se ha senso andare avanti ti inviamo una <strong>proposta scritta</strong> con servizi, workflow inclusi, tempi, prezzo e condizioni di pagamento. L'accordo si conclude quando accetti la proposta per iscritto, anche via email.</p>'''),
        ("automazione", "I servizi di automazione", '''
<h3>Come si paga</h3>
<p>I pacchetti di automazione hanno un <strong>costo di avvio una tantum</strong>, per progettazione e configurazione, e poi un <strong>canone mensile</strong> per l'esercizio, la sorveglianza e la manutenzione. Le aggiunte si attivano e si disattivano su base mensile.</p>
<h3>Durata e disdetta</h3>
<p>Il canone ha una durata minima di <strong>tre mesi</strong>. Passati i primi tre mesi puoi disdire quando vuoi, con le modalità e il preavviso indicati nella proposta. Il costo di avvio copre lavoro già svolto e non viene rimborsato.</p>
<h3>Il controllo resta a te</h3>
<p>I sistemi di Octagon preparano il lavoro e ti chiedono l'approvazione prima di ogni azione che conta: pubblicare, inviare, cambiare un prezzo, spendere. <strong>Le azioni approvate sono decisioni tue</strong>: prima di approvare controlla quello che ti viene proposto. I contenuti prodotti dall'AI possono contenere errori, ed è proprio per questo che passano da te.</p>
<p>I controlli deterministici concordati, come prezzi minimi, limiti di spesa e regole del marchio, sono scritti nel codice e li manteniamo attivi per tutta la durata del servizio.</p>'''),
        ("web", "Siti e applicazioni su misura", '''
<p>Per landing page, negozi Shopify e applicazioni su misura i tempi del listino sono indicativi e partono da quando riceviamo tutto il materiale necessario (testi da approvare, immagini, accessi). Sono compresi i giri di revisione indicati nella proposta; le richieste che vanno oltre si concordano a parte.</p>
<p>Salvo accordi diversi nella proposta, quando il lavoro è saldato ricevi i diritti per usare e modificare liberamente il sito o l'applicazione realizzati per te. Restano di Octagon gli strumenti, i componenti e i metodi che usiamo anche per altri clienti.</p>'''),
        ("cliente", "Cosa ti chiediamo", '''
<ul>
<li>Darci gli accessi e le informazioni che servono, e tenerli aggiornati.</li>
<li>Avere i diritti su testi, immagini, marchi e dati che ci affidi, e usarli nel rispetto della legge.</li>
<li>Rispettare le regole delle piattaforme collegate al servizio, come Shopify, Klaviyo, Vinted o Telegram.</li>
<li>Non usare i servizi per attività illecite, spam o contenuti ingannevoli.</li>
</ul>'''),
        ("terzi", "Piattaforme di terze parti", '''
<p>I servizi si collegano a piattaforme di altri (negozi online, marketplace, email marketing, messaggistica). Le loro condizioni, i loro prezzi e la loro disponibilità non dipendono da noi. Se una piattaforma cambia regole o interfacce adattiamo i workflow nel più breve tempo possibile, ma non rispondiamo dei disservizi della piattaforma.</p>'''),
        ("responsabilita", "Responsabilità", '''
<p>Lavoriamo con cura professionale e sorvegliamo i sistemi che gestiamo. Nei limiti consentiti dalla legge, e salvo i casi di dolo o colpa grave (art. 1229 del Codice civile), la nostra responsabilità per danni legati ai servizi è limitata all'importo che ci hai pagato nei 12 mesi precedenti al fatto. Non rispondiamo delle conseguenze di azioni che hai approvato tu né dei mancati guadagni indiretti.</p>
<p>Il sito è offerto così com'è: facciamo il possibile perché sia sempre disponibile e corretto, ma possono capitare interruzioni o imprecisioni.</p>'''),
        ("pagamenti", "Pagamenti", '''
<p>Modalità e scadenze di pagamento sono indicate nella proposta. In caso di ritardo, tra imprese si applicano gli interessi previsti dal D.Lgs. 231/2002. Se un pagamento resta in sospeso oltre 30 giorni dalla scadenza possiamo sospendere il servizio dopo avertelo comunicato per iscritto.</p>'''),
        ("proprieta", "Proprietà intellettuale del sito", '''
<p>Testi, grafica, immagini, logo e codice di questo sito appartengono a Octagon o sono usati con licenza. Puoi condividere i link alle pagine, ma non puoi copiarne i contenuti per altri usi senza il nostro permesso scritto. I caratteri tipografici sono distribuiti con licenza SIL Open Font License.</p>'''),
        ("riservatezza", "Riservatezza e dati personali", '''
<p>Trattiamo come riservate le informazioni sulla tua attività che conosciamo lavorando insieme e le usiamo solo per erogare il servizio. Quando i nostri sistemi trattano dati personali dei tuoi clienti agiamo come responsabile del trattamento, con un accordo scritto ai sensi dell'art. 28 del GDPR. Il resto è spiegato nell'<a href="/privacy">informativa privacy</a>.</p>'''),
        ("legge", "Legge applicabile e foro", f'''
<p>Questi termini sono regolati dalla legge italiana. {foro_frase()} Se sei un consumatore è competente il giudice del luogo in cui risiedi.</p>
<p>Puoi aggiornare questi termini solo con un accordo scritto; noi possiamo aggiornare questa pagina, ma le modifiche non si applicano ai contratti già in corso senza il tuo consenso. Versione in vigore dal {AGGIORNATO}.</p>'''),
    ]
    brief = [
        "Il sito presenta i servizi: <strong>vale la proposta scritta</strong> che firmi.",
        "Automazione: <strong>costo di avvio e canone mensile</strong>, disdicibile passati i primi tre mesi.",
        "<strong>Ogni azione che conta passa da te</strong>: le approvazioni sono decisioni tue.",
        "Siti su misura: al saldo puoi <strong>usare e modificare liberamente</strong> il lavoro consegnato.",
        "Servizi pensati per <strong>imprese e professionisti</strong>, regolati dalla legge italiana.",
    ]
    return page("/termini", "Termini di servizio",
                "Le condizioni d'uso del sito di Octagon e le condizioni generali dei servizi di automazione e web creation.",
                "Note legali · Termini", 'Le regole del <em class="s">lavoro insieme.</em>',
                "Condizioni d'uso del sito e condizioni generali dei servizi Octagon. Brevi dove possibile, precise dove serve.",
                brief, s)


def aggiorna_footer_sito():
    """Allinea la riga in fondo al piede di home e listino con titolare e P.IVA."""
    nuovo = f'<div class="foot-bottom"><span>{foot_bottom()}</span>'
    for f in ("index.html", "pricing.html"):
        p = ROOT / f
        s = p.read_text()
        s2 = re.sub(r'<div class="foot-bottom"><span>.*?</span>', nuovo, s, count=1, flags=re.S)
        if s2 != s:
            p.write_text(s2)


if __name__ == "__main__":
    for name, fn in (("privacy.html", privacy), ("cookie.html", cookie), ("termini.html", termini)):
        (ROOT / name).write_text(fn())
    aggiorna_footer_sito()
    m = mancanti()
    print("Generate: privacy.html, cookie.html, termini.html")
    print("Dati mancanti:", ", ".join(m) if m else "nessuno")
