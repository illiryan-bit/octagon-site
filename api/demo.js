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
  };
  const errors = {};
  if (d.name.length < 2) errors.name = 'Scrivi il tuo nome.';
  if (!EMAIL_RE.test(d.email)) errors.email = "Serve un'email valida.";
  if (Object.keys(errors).length) return send(res, 422, { ok: false, error: 'invalid', fields: errors });

  if (!process.env.RESEND_API_KEY) {
    console.error('[demo] RESEND_API_KEY mancante');
    return send(res, 503, { ok: false, error: 'not_configured' });
  }

  const when = new Intl.DateTimeFormat('it-IT', { dateStyle: 'full', timeStyle: 'short', timeZone: 'Europe/Rome' }).format(new Date());
  const rows = [['Nome', d.name], ['Email', d.email], ['Attività', d.company || '—'], ['Piano di interesse', d.plan || '—']];
  const text = `Nuova richiesta di demo dal sito — ${when}\n\n` +
    rows.map(([k, v]) => `${k}: ${v}`).join('\n') +
    `\n\nIl lavoro che si ripete:\n${d.work || '—'}\n\nRispondi a questa email per scrivere direttamente a ${d.name}.`;
  const html = `<div style="font-family:Arial,Helvetica,sans-serif;color:#1b1b1b;max-width:560px">
<p style="font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#1F7A74;margin:0 0 6px">Octagon · richiesta demo</p>
<h1 style="font-size:20px;margin:0 0 16px">${esc(d.name)}${d.company ? ' · ' + esc(d.company) : ''}</h1>
<table style="border-collapse:collapse;font-size:14px;width:100%">${rows.map(([k, v]) => `<tr><td style="padding:6px 12px 6px 0;color:#666;white-space:nowrap;vertical-align:top">${k}</td><td style="padding:6px 0">${k === 'Email' ? `<a href="mailto:${esc(v)}">${esc(v)}</a>` : esc(v)}</td></tr>`).join('')}</table>
<p style="font-size:13px;color:#666;margin:18px 0 6px">Il lavoro che si ripete</p>
<div style="font-size:14px;line-height:1.5;white-space:pre-wrap;background:#F4EFE8;border-radius:10px;padding:12px 14px">${esc(d.work || '—')}</div>
<p style="font-size:12px;color:#888;margin-top:18px">${esc(when)} · Rispondi a questa email per scrivere direttamente a chi ha fatto la richiesta.</p></div>`;

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: FROM, to: [TO], reply_to: d.email,
        subject: `Richiesta demo: ${d.name}${d.company ? ' — ' + d.company : ''}`.slice(0, 180),
        text, html,
      }),
    });
    if (!r.ok) {
      console.error('[demo] Resend', r.status, (await r.text()).slice(0, 500));
      return send(res, 502, { ok: false, error: 'send' });
    }
    return send(res, 200, { ok: true });
  } catch (e) {
    console.error('[demo] errore di rete', e && e.message);
    return send(res, 502, { ok: false, error: 'send' });
  }
};
