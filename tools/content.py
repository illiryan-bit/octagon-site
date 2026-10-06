"""Contenuti condivisi del sito OCTAGON: servizi, aree, pagina Reti, testi SEO.

Fonte: documento «OCTAGON — Aggiornamento sito» (6 ottobre 2026). I testi dei servizi sono
quelli del documento; non aggiungere servizi, prezzi, clienti o numeri che non siano lì.

Usato da tools/build_pages.py per generare:
  - servizi/<slug>.html e reti.html
  - l'elenco dei servizi nella sezione «Cosa fa» della home (tra i marcatori @services)
  - sitemap.xml, robots.txt, llms.txt
"""

SITE = "https://theoctagonai.com"
EMAIL = "info@theoctagonai.com"

# Interruttore: la pagina Reti di partner è pronta ma la pubblicazione dipende da una tua scelta
# (documento, «Da decidere»). Con False la pagina non viene generata né collegata.
SHOW_RETI = False

# Lingue servite dai dati strutturati (documento, sezione SEO)
AREA_SERVED = ["Italia", "Spagna", "Stati Uniti"]

AREAS = [
    ("vendere", "Vendere", "#4FA89A"),
    ("trovare", "Farsi trovare", "#7FA7E0"),
    ("comunicare", "Comunicare", "#8C7CE0"),
    ("costruire", "Costruire", "#101418"),
]

# ok: True se il servizio ha un passaggio di approvazione (mostra il rombo coral)
SERVICES = [
    dict(slug="automazione", area="vendere", name="Automazione operativa", short="Automazione", color="#5FB3A8", ok=True,
         what="Ordini, catalogo, prezzi, documenti e richieste preparati dal sistema.",
         you="Prezzi, pubblicazioni, invii ai clienti.",
         replaces="Ore di lavoro a mano ogni settimana.",
         where=["Il tuo negozio", "Marketplace", "Email", "Telegram"],
         title="Automazione operativa con agenti AI · OCTAGON",
         desc="Ordini, catalogo, prezzi, documenti e richieste preparati da agenti AI. Prezzi, pubblicazioni e invii ai clienti partono solo con il tuo ok."),
    dict(slug="shopify", area="vendere", name="Negozio Shopify", short="Shopify", color="#8FD3CC", ok=True,
         what="Recensioni, traduzioni, upsell, moduli e chat svolti dal sistema, senza app a pagamento.",
         you="Ogni modifica al negozio.",
         replaces="Le app a pagamento, tema escluso.",
         where=["Shopify"],
         title="Negozio Shopify senza app a pagamento · OCTAGON",
         desc="Recensioni, traduzioni, upsell, moduli e chat svolti dal sistema al posto delle app a pagamento. Ogni modifica al negozio passa dal tuo ok."),
    dict(slug="amazon", area="vendere", name="Amazon", short="Amazon", color="#F0B08A", ok=True,
         what="Schede e contenuti A+, prezzi e Buy Box, scorte, recensioni, collegati allo store Shopify.",
         you="Prezzi, schede, spesa in Amazon Ads.",
         replaces="Gestione esterna dello store.",
         where=["Amazon", "Amazon Ads", "Shopify"],
         title="Gestione store Amazon con agenti AI · OCTAGON",
         desc="Schede, prezzi, Amazon Ads e recensioni gestiti nello stesso sistema del tuo negozio Shopify, con il tuo ok."),
    dict(slug="seo-visibilita-ai", area="trovare", name="SEO e visibilità AI", short="SEO e visibilità AI", color="#7FA7E0", ok=True,
         what="Testi, pagine e dati strutturati per Google e per gli assistenti AI, in più lingue.",
         you="Ogni lotto di modifiche.",
         replaces="Agenzia SEO e strumenti in abbonamento.",
         where=["Google", "ChatGPT", "Gemini", "Perplexity"],
         title="SEO e visibilità sugli assistenti AI · OCTAGON",
         desc="Pagine e dati strutturati per Google, ChatGPT, Gemini e Perplexity, in più lingue. Ogni modifica approvata da te."),
    dict(slug="analisi", area="trovare", name="Analisi di mercato", short="Analisi di mercato", color="#A9C3EE", ok=False,
         what="Concorrenti, prezzi, recensioni e risultati, in un report ogni lunedì.",
         you="Nessuno: solo lettura.",
         replaces="Strumenti di monitoraggio in abbonamento.",
         where=["Telegram", "Email"],
         title="Analisi di mercato settimanale · OCTAGON",
         desc="Concorrenti, prezzi, recensioni e risultati raccolti dal sistema e consegnati in un report ogni lunedì. Solo lettura, nessuna azione."),
    dict(slug="social", area="comunicare", name="Social e shop", short="Social e shop", color="#B3A6EE", ok=True,
         what="Piano editoriale, pubblicazione su Instagram, Facebook, TikTok e LinkedIn, catalogo shop sincronizzato.",
         you="Ogni post prima che esca.",
         replaces="Social media manager esterno.",
         where=["Instagram", "Facebook", "TikTok", "LinkedIn"],
         title="Social e shop gestiti con agenti AI · OCTAGON",
         desc="Piano editoriale, pubblicazione su Instagram, Facebook, TikTok e LinkedIn e catalogo shop sincronizzato. Ogni post esce solo con il tuo ok."),
    dict(slug="campagne", area="comunicare", name="Campagne", short="Campagne", color="#8C7CE0", ok=True,
         what="Meta, Google, TikTok e Amazon Ads dentro un limite di spesa fissato da te.",
         you="Ogni variazione di budget.",
         replaces="Gestione campagne in agenzia.",
         where=["Meta", "Google", "TikTok", "Amazon Ads"],
         title="Campagne Meta, Google, TikTok e Amazon Ads · OCTAGON",
         desc="Campagne su Meta, Google, TikTok e Amazon Ads seguite dentro un limite di spesa fissato da te. Ogni variazione di budget passa dal tuo ok."),
    dict(slug="fotovideo", area="comunicare", name="Foto e video in sede", short="Foto e video", color="#D9A7E8", ok=True,
         what="Foto prodotto, scene e video brevi creati sulla nostra infrastruttura, senza costo per singolo file.",
         you="Ogni contenuto prima dell'uso.",
         replaces="Servizi di generazione a pagamento, servizi fotografici ripetuti.",
         where=["Il tuo negozio", "Social", "Campagne"],
         title="Foto e video di prodotto creati in sede · OCTAGON",
         desc="Foto e video del tuo marchio creati sulla nostra infrastruttura, senza abbonamenti per immagine."),
    dict(slug="clienti", area="comunicare", name="Servizio clienti e traduzioni", short="Clienti e traduzioni", color="#F5C6A5", ok=True,
         what="Bozze di risposta, preventivi, testi tradotti in cinque lingue.",
         you="Ogni risposta prima dell'invio.",
         replaces="Chat a pagamento, traduttori per ogni testo.",
         where=["Email", "Il tuo negozio", "Telegram"],
         title="Servizio clienti e traduzioni con agenti AI · OCTAGON",
         desc="Bozze di risposta, preventivi e testi tradotti in cinque lingue, preparati dal sistema. Ogni risposta parte solo dopo il tuo ok."),
    dict(slug="siti", area="costruire", name="Siti, negozi e app", short="Siti, negozi e app", color="#101418", ok=True, dark=True,
         what="Landing page, negozi Shopify, applicazioni su misura, collegati al sistema.",
         you="Ogni rilascio.",
         replaces=None,
         where=["Il tuo dominio", "Shopify"],
         title="Siti, negozi Shopify e app su misura · OCTAGON",
         desc="Landing page, negozi Shopify e applicazioni su misura, collegati allo stesso sistema di agenti AI. Ogni rilascio passa dal tuo ok."),
]

RETI = dict(
    title="Un sistema per tutta la rete di partner · OCTAGON",
    desc="Gli stessi servizi per distributori e punti vendita in più paesi, con il marchio e le regole della casa madre.",
    h1="Un marchio, molti punti vendita.",
    h1s="Un sistema per tutti.",
    text=("Per i marchi con distributori, bar, negozi e partner in più paesi. Ogni partner riceve gli stessi servizi, "
          "con le regole e l'identità della casa madre: schede e listini allineati, contenuti nel marchio, "
          "campagne locali dentro un budget approvato. Si parte con un pilota di 3–5 partner per 90 giorni."),
    cta="Parliamone",
    plan="Reti",
)

HOME_FAQ = [
    ("Che cos'è Octagon?", "Octagon è uno studio founder-led che costruisce e gestisce sistemi di agenti AI per il lavoro operativo di aziende e brand: negozio online, Amazon, SEO, social, campagne, foto e video, servizio clienti. Il sistema prepara il lavoro; ogni azione che conta parte solo dopo la tua approvazione su Telegram."),
    ("Con quali piattaforme lavorate?", "Shopify, Amazon, Etsy, Vinted e Grailed; Google e gli assistenti AI; Instagram, Facebook, TikTok e LinkedIn; Meta, Google, TikTok e Amazon Ads; Klaviyo per l'email. Se usi strumenti diversi, lo verifichiamo nella call prima di iniziare."),
    ("Quanto tempo serve per partire?", "Si parte da una call di 20 minuti e da un solo lavoro ripetuto. Con il pacchetto Starter l'avvio richiede 3–5 giorni; nei pacchetti più ampi la configurazione la seguiamo noi."),
    ("Devo cambiare gli strumenti che uso?", "No. Octagon lavora sui canali e sugli strumenti che hai già. Con il sistema parli su Telegram."),
    ("Cosa succede se l'AI sbaglia?", "Prima di tutto la ferma una regola scritta nel codice, come un prezzo minimo o un limite di spesa. Poi ogni azione con una conseguenza aspetta il tuo ok. Nulla esce senza di te."),
    ("Dove girano i flussi e dove restano i dati?", "Su infrastruttura gestita da Octagon: orchestrazione, database e memoria sono self-hosted. Ti spieghiamo nel dettaglio cosa passa da servizi esterni durante la call."),
    ("Lavorate anche con aziende grandi o con reti di negozi?", "Sì. Lo stesso sistema serve un negozio singolo e un marchio con partner in più paesi: ogni sede ha le sue regole, il marchio resta uno."),
    ("Foto e video: da dove arrivano?", "Li creiamo in sede, sulla nostra infrastruttura, a partire dalle vostre foto e dalle regole visive del marchio. Nessun abbonamento a servizi esterni per ogni immagine."),
    ("Fate anche siti e negozi online?", "Sì. Landing page, negozi Shopify e applicazioni su misura, collegati allo stesso sistema. E gestiamo lo store su Amazon nello stesso sistema."),
    ("Quanto costa?", "Dipende da cosa prende in carico il sistema. Trovi le formule nel listino."),
]


def area(key):
    return next(a for a in AREAS if a[0] == key)


def services_in(key):
    return [s for s in SERVICES if s["area"] == key]

# WhatsApp Business: pulsante «Scrivici su WhatsApp» (link wa.me, nessun server in mezzo)
WHATSAPP = "393496899846"
WHATSAPP_TEXT = "Ciao Octagon, vorrei sapere cosa può prendere in carico il sistema per la mia attività."
