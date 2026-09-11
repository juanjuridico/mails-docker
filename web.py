from flask import Flask, jsonify, render_template_string, request
from db import get_emails as db_get_emails, get_email_by_email
from email_service import generate_email, get_emails, delete_email
from tempmailg_api import TempMailGAPIError, TempMailGAPI

app = Flask(__name__)

HTML = r'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Correos temporales</title><style>
body{font-family:system-ui,sans-serif;max-width:1000px;margin:40px auto;padding:0 18px;background:#f5f7fb;color:#172033}
.card{background:white;border-radius:16px;padding:22px;margin:14px 0;box-shadow:0 5px 25px #0001}.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
button{border:0;border-radius:10px;padding:10px 15px;background:#172033;color:white;cursor:pointer}button.danger{background:#a22}button:disabled{opacity:.5}
.email{font-family:ui-monospace,monospace;font-size:1.05rem;padding:12px;background:#eef2ff;border-radius:10px;flex:1}.muted{color:#687386}.msg{border-top:1px solid #eee;padding:14px 0}.error{color:#a22}.ok{color:#176b3a}
</style></head><body><h1>Correos temporales</h1><p class="muted">TempMailG · API oficial</p>
<div class="card"><div class="row"><button onclick="newMail()">+ Generar correo</button><button onclick="loadMails()">Actualizar</button><span id="status" class="muted"></span></div></div>
<div id="mails"></div><div id="inbox"></div>
<script>
const esc=s=>String(s??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
async function api(url,opt){let r=await fetch(url,opt);let d=await r.json();if(!r.ok||d.ok===false)throw Error(d.error||d.message||'Error');return d}
async function newMail(){setStatus('Generando...');try{let d=await api('/api/emails',{method:'POST'});setStatus('Correo creado','ok');loadMails();openInbox(d.data.email)}catch(e){setStatus(e.message,'error')}}
async function loadMails(){try{let d=await api('/api/emails');document.querySelector('#mails').innerHTML=d.data.map(x=>`<div class="card row"><div class="email">${esc(x.email)}</div><button onclick="openInbox('${encodeURIComponent(x.email)}')">Bandeja</button><button class="danger" onclick="removeMail('${encodeURIComponent(x.email)}')">Eliminar</button></div>`).join('')||'<div class="card muted">No hay correos activos.</div>'}catch(e){setStatus(e.message,'error')}}
async function openInbox(e){e=decodeURIComponent(e);try{let d=await api('/api/emails/'+encodeURIComponent(e)+'/messages');document.querySelector('#inbox').innerHTML=`<div class="card"><h2>${esc(e)}</h2>${d.data.length?d.data.map(m=>`<div class="msg"><b>${esc(m.subject||'(sin asunto)')}</b><div>De: ${esc(m.from_email||m.from||'')}</div><div class="muted">${esc(m.receivedAt||m.date||'')}</div><div>${m.html?m.content:(esc(m.content||m.body||''))}</div></div>`).join(''):'<p class="muted">No hay mensajes todavía.</p>'}</div>`}catch(err){setStatus(err.message,'error')}}
async function removeMail(e){e=decodeURIComponent(e);if(!confirm('¿Eliminar '+e+'?'))return;try{await api('/api/emails/'+encodeURIComponent(e),{method:'DELETE'});loadMails();document.querySelector('#inbox').innerHTML=''}catch(err){setStatus(err.message,'error')}}
function setStatus(s,c='muted'){let x=document.querySelector('#status');x.textContent=s;x.className=c}loadMails();
</script></body></html>'''


def configured_error():
    if TempMailGAPI().configured:
        return None
    return "TempMailG API no configurada: agrega TEMPMAILG_API_KEY al .env de mails-docker. La web pública está protegida por Cloudflare Turnstile y no se intenta evadirlo."


@app.get("/")
def index():
    return render_template_string(HTML)


@app.get("/health")
def health():
    import os
    return jsonify({"service": "mails-docker", "status": "ok", "tempmailg_api_configured": TempMailGAPI().configured, "vpn_proxy_configured": bool(os.getenv("PROXY"))})


@app.get("/api/emails")
def list_api():
    return jsonify({"ok": True, "data": db_get_emails(provider=None, is_active=True)})


@app.post("/api/emails")
def create_api():
    try:
        if not TempMailGAPI().configured:
            raise TempMailGAPIError("TEMPMAILG_API_KEY no está configurada. Crea una API key en el panel de TempMailG y agrégala al .env de mails-docker.")
        email = generate_email(provider="tempmailg")
        if not email:
            raise TempMailGAPIError("TempMailG no devolvió un correo")
        return jsonify({"ok": True, "data": {"email": email}}), 201
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503


@app.get("/api/emails/<path:email>/messages")
def messages_api(email):
    try:
        if not TempMailGAPI().configured:
            raise TempMailGAPIError("TEMPMAILG_API_KEY no está configurada. Crea una API key en el panel de TempMailG y agrégala al .env de mails-docker.")
        if not get_email_by_email(email):
            return jsonify({"ok": False, "error": "Correo no encontrado"}), 404
        return jsonify({"ok": True, "data": get_emails(email, provider="tempmailg")})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503


@app.delete("/api/emails/<path:email>")
def delete_api(email):
    try:
        return jsonify({"ok": delete_email(email, provider="tempmailg")})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
