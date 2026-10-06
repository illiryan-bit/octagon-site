// Vercel Node function: POST /api/demo
// Riceve il modulo "Prenota una demo" e lo inoltra via Resend a info@theoctagonai.com.
// Variabili d'ambiente (Vercel → Settings → Environment Variables):
//   RESEND_API_KEY  obbligatoria
//   MAIL_FROM       mittente su dominio verificato in Resend, es. "Octagon <sito@theoctagonai.com>"
//   MAIL_TO         destinatario (predefinito info@theoctagonai.com)

const TO = process.env.MAIL_TO || 'info@theoctagonai.com';
const FROM = process.env.MAIL_FROM || 'Octagon <sito@theoctagonai.com>';
const EMAIL_RE = /^[^\s@<>"]+@[^\s@<>"]+\.[^\s@<>"]{2,}$/;
const LIMITS = { name: 120, email: 200, company: 200, work: 4000, plan: 80 };
const KINDS = { demo: 'Demo', offerta: 'Offerta su misura' };

// Slot delle call: lun–ven, 14:00–17:40 ogni 20 minuti (durata 20'), ora italiana, dal giorno lavorativo successivo
// fino a 21 giorni. Le stesse regole sono nel modulo (index.html).
const HOLIDAYS = new Set(['2026-11-01','2026-12-08','2026-12-25','2026-12-26','2027-01-01','2027-01-06','2027-03-29','2027-04-25','2027-05-01','2027-06-02','2027-08-15','2027-11-01','2027-12-08','2027-12-25','2027-12-26']);
const SLOT_TIMES = new Set(); for (let m = 14 * 60; m <= 17 * 60 + 40; m += 20) SLOT_TIMES.add(String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0'));
const romeParts = (date) => Object.fromEntries(new Intl.DateTimeFormat('en-US', { timeZone: 'Europe/Rome', hourCycle: 'h23', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }).formatToParts(date).map(p => [p.type, p.value]));
const romeOffsetMin = (date) => { const r = romeParts(date); return (Date.UTC(+r.year, +r.month - 1, +r.day, +r.hour, +r.minute) - Math.floor(date.getTime() / 6e4) * 6e4) / 6e4; };
function slotDate(day, time) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day) || !SLOT_TIMES.has(time)) return null;
  const [y, m, d] = day.split('-').map(Number), [hh, mm] = time.split(':').map(Number);
  const local = Date.UTC(y, m - 1, d, hh, mm), wd = new Date(Date.UTC(y, m - 1, d)).getUTCDay();
  if (wd === 0 || wd === 6 || HOLIDAYS.has(day)) return null;
  let t = local - romeOffsetMin(new Date(local)) * 6e4; t = local - romeOffsetMin(new Date(t)) * 6e4;
  const r = romeParts(new Date()), today = `${r.year}-${r.month}-${r.day}`;
  if (day <= today || t - Date.now() > 21 * 864e5) return null;
  return new Date(t);
}
const dayLabel = (day) => new Intl.DateTimeFormat('it-IT', { timeZone: 'UTC', weekday: 'long', day: 'numeric', month: 'long' }).format(new Date(day + 'T12:00:00Z'));
const icsDate = (d) => d.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
const icsText = (v) => String(v).replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\r?\n/g, '\\n');
function ics({ start, summary, description, attendee }) {
  const end = new Date(start.getTime() + 20 * 6e4);
  return ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Octagon//Sito//IT', 'METHOD:PUBLISH', 'BEGIN:VEVENT',
    `UID:${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}@theoctagonai.com`, `DTSTAMP:${icsDate(new Date())}`,
    `DTSTART:${icsDate(start)}`, `DTEND:${icsDate(end)}`, `SUMMARY:${icsText(summary)}`, `DESCRIPTION:${icsText(description)}`,
    attendee ? `ATTENDEE;CN=${icsText(attendee.name)}:mailto:${attendee.email}` : null, 'END:VEVENT', 'END:VCALENDAR'].filter(Boolean).join('\r\n');
}

const hits = new Map(); // limite semplice per istanza: 5 invii / 10 minuti per IP
function limited(ip) {
  const now = Date.now(), win = 10 * 60 * 1000;
  const arr = (hits.get(ip) || []).filter((t) => now - t < win);
  arr.push(now); hits.set(ip, arr);
  return arr.length > 5;
}

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const clean = (v, max) => (typeof v === 'string' ? v.replace(/\r\n?/g, '\n').trim().slice(0, max) : '');

async function readBody(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  if (typeof req.body === 'string') { try { return JSON.parse(req.body); } catch { return {}; } }
  const chunks = []; for await (const c of req) chunks.push(c);
  try { return JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}'); } catch { return {}; }
}

function send(res, status, data) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(data));
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return send(res, 405, { ok: false, error: 'method' }); }

  const origin = req.headers.origin || '';
  if (origin && !/^https:\/\/(www\.)?theoctagonai\.com$|^https:\/\/[a-z0-9-]+\.vercel\.app$|^http:\/\/localhost(:\d+)?$/.test(origin)) {
    return send(res, 403, { ok: false, error: 'origin' });
  }

  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
  if (limited(ip)) return send(res, 429, { ok: false, error: 'rate' });

  const b = await readBody(req);
  // Anti-spam: campo nascosto compilato o invio troppo rapido → fingiamo successo e scartiamo.
  const elapsed = Date.now() - Number(b.t || 0);
  if (clean(b.website, 200) || !(elapsed > 2500 && elapsed < 864e5)) return send(res, 200, { ok: true });

  const d = {
    name: clean(b.name, LIMITS.name),
    email: clean(b.email, LIMITS.email).toLowerCase(),
    company: clean(b.company, LIMITS.company),
    work: clean(b.work, LIMITS.work),
    plan: clean(b.plan, LIMITS.plan),
    kind: KINDS[b.kind] ? b.kind : 'demo',
    day: clean(b.day, 10),
    time: clean(b.time, 5),
  };
  const start = slotDate(d.day, d.time);
  const errors = {};
  if (d.name.length < 2) errors.name = 'Scrivi il tuo nome.';
  if (!EMAIL_RE.test(d.email)) errors.email = "Serve un'email valida.";
  if (!d.day) errors.day = 'Scegli il giorno della call.';
  if (!d.time) errors.time = "Scegli l'orario.";
  else if (!SLOT_TIMES.has(d.time)) errors.time = 'Scegli un orario tra le 14:00 e le 17:40.';
  if (d.day && !errors.time && !start) errors.day = 'Questo giorno non è disponibile: scegline un altro.';
  if (Object.keys(errors).length) return send(res, 422, { ok: false, error: 'invalid', fields: errors });

  if (!process.env.RESEND_API_KEY) {
    console.error('[demo] RESEND_API_KEY mancante');
    return send(res, 503, { ok: false, error: 'not_configured' });
  }

  const when = new Intl.DateTimeFormat('it-IT', { dateStyle: 'full', timeStyle: 'short', timeZone: 'Europe/Rome' }).format(new Date());
  const kind = KINDS[d.kind], slot = `${dayLabel(d.day)} alle ${d.time}`;
  const rows = [['Richiesta', kind], ['Call', `${slot} (ora italiana, 20 minuti)`], ['Nome', d.name], ['Email', d.email], ['Attività', d.company || '—'], ['Piano di interesse', d.plan || '—']];
  const text = `Nuova richiesta dal sito (${kind}) — ${when}\n\n` +
    rows.map(([k, v]) => `${k}: ${v}`).join('\n') +
    `\n\nIl lavoro che si ripete:\n${d.work || '—'}\n\nRispondi a questa email per scrivere direttamente a ${d.name}.`;
  const html = `<div style="font-family:Arial,Helvetica,sans-serif;color:#1b1b1b;max-width:560px">
<p style="font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#1F7A74;margin:0 0 6px">Octagon · ${esc(kind.toLowerCase())}</p>
<h1 style="font-size:20px;margin:0 0 16px">${esc(d.name)}${d.company ? ' · ' + esc(d.company) : ''}</h1>
<table style="border-collapse:collapse;font-size:14px;width:100%">${rows.map(([k, v]) => `<tr><td style="padding:6px 12px 6px 0;color:#666;white-space:nowrap;vertical-align:top">${k}</td><td style="padding:6px 0">${k === 'Email' ? `<a href="mailto:${esc(v)}">${esc(v)}</a>` : esc(v)}</td></tr>`).join('')}</table>
<p style="font-size:13px;color:#666;margin:18px 0 6px">Il lavoro che si ripete</p>
<div style="font-size:14px;line-height:1.5;white-space:pre-wrap;background:#F4EFE8;border-radius:10px;padding:12px 14px">${esc(d.work || '—')}</div>
<p style="font-size:12px;color:#888;margin-top:18px">${esc(when)} · Rispondi a questa email per scrivere direttamente a chi ha fatto la richiesta.</p></div>`;

  const invite = Buffer.from(ics({ start, summary: `Call Octagon · ${d.name} (${kind})`, description: `${kind} — ${d.name}${d.company ? ', ' + d.company : ''}\n${d.email}\n\n${d.work || ''}`, attendee: { name: d.name, email: d.email } })).toString('base64');
  const resend = (body) => fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  try {
    const r = await resend({
      from: FROM, to: [TO], reply_to: d.email,
      subject: `${kind}: ${d.name}${d.company ? ' — ' + d.company : ''} · ${slot}`.slice(0, 180),
      text, html, attachments: [{ filename: 'call-octagon.ics', content: invite }],
    });
    if (!r.ok) {
      console.error('[demo] Resend', r.status, (await r.text()).slice(0, 500));
      return send(res, 502, { ok: false, error: 'send' });
    }
    // Riepilogo a chi ha fatto la richiesta: non blocca la risposta se fallisce.
    const first = d.name.split(/\s+/)[0];
    const cText = `Ciao ${first},\n\nabbiamo ricevuto la tua richiesta (${kind.toLowerCase()}) per una call di 20 minuti ${slot}, ora italiana.\n\nTi confermiamo l'appuntamento entro un giorno lavorativo. Se l'orario non va più bene, rispondi a questa email.\n\nOctagon\nhttps://theoctagonai.com`;
    const cHtml = `<div style="font-family:Arial,Helvetica,sans-serif;color:#1b1b1b;max-width:520px;font-size:15px;line-height:1.55"><p style="font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#1F7A74;margin:0 0 10px">Octagon</p><p>Ciao ${esc(first)},</p><p>abbiamo ricevuto la tua richiesta (${esc(kind.toLowerCase())}) per una call di 20 minuti:</p><p style="background:#F4EFE8;border-radius:10px;padding:12px 14px;font-weight:bold">${esc(slot)}, ora italiana</p><p>Ti confermiamo l'appuntamento entro un giorno lavorativo. Se l'orario non va più bene, rispondi a questa email.</p><p style="color:#666;font-size:13px">Octagon · <a href="https://theoctagonai.com">theoctagonai.com</a></p></div>`;
    try {
      const c = await resend({ from: FROM, to: [d.email], reply_to: TO, subject: `Richiesta ricevuta: call ${slot}`.slice(0, 180), text: cText, html: cHtml });
      if (!c.ok) console.error('[demo] riepilogo', c.status, (await c.text()).slice(0, 300));
    } catch (e) { console.error('[demo] riepilogo rete', e && e.message); }
    return send(res, 200, { ok: true });
  } catch (e) {
    console.error('[demo] errore di rete', e && e.message);
    return send(res, 502, { ok: false, error: 'send' });
  }
};
