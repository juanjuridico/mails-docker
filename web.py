from flask import Flask, jsonify, render_template_string, request
from db import get_emails as db_get_emails, get_email_by_email
from email_service import generate_email, get_emails, delete_email
from tempmailg_api import TempMailGAPIError, TempMailGAPI
import mailtm_provider
import free_temp_provider
import emailnator_provider

app = Flask(__name__)

HTML = r'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Correos temporales</title><style>
body{font-family:system-ui,sans-serif;max-width:1000px;margin:40px auto;padding:0 18px;background:#f5f7fb;color:#172033}
.card{background:white;border-radius:16px;padding:22px;margin:14px 0;box-shadow:0 5px 25px #0001}.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
button{border:0;border-radius:10px;padding:10px 15px;background:#172033;color:white;cursor:pointer}button.danger{background:#a22}button:disabled{opacity:.5}
.email{font-family:ui-monospace,monospace;font-size:1.05rem;padding:12px;background:#eef2ff;border-radius:10px;flex:1}.email-body{overflow:auto;background:#fff;border-radius:10px;padding:12px}.email-body img{max-width:100%;height:auto}.email-body a{color:#1565c0}.muted{color:#687386}.msg{border-top:1px solid #eee;padding:14px 0}.error{color:#a22}.ok{color:#176b3a}
</style></head><body><h1>Correos temporales</h1><p class="muted">Gmail temporal · @gmail.com sin API key</p>
<div class="card"><div class="row"><button onclick="newMail()">+ Generar correo</button><button onclick="loadMails()">Actualizar</button><span id="status" class="muted"></span></div><p class="muted" id="mode">Inicializando…</p></div>
<div id="mails"></div><div id="inbox"></div>
<script>
const esc=s=>String(s??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
async function api(url,opt){let r=await fetch(url,opt);let d=await r.json();if(!r.ok||d.ok===false)throw Error(d.error||d.message||'Error');return d}
async function newMail(){setStatus('Generando...');try{let d=await api('/api/emails',{method:'POST'});setStatus('Correo creado','ok');loadMails();openInbox(d.data.email)}catch(e){setStatus(e.message,'error')}}
async function loadMails(){try{let d=await api('/api/emails');document.querySelector('#mails').innerHTML=d.data.map(x=>`<div class="card row"><div class="email">${esc(x.email)}</div><button onclick="openInbox('${encodeURIComponent(x.email)}')">Bandeja</button><button class="danger" onclick="removeMail('${encodeURIComponent(x.email)}')">Eliminar</button></div>`).join('')||'<div class="card muted">No hay correos activos.</div>'}catch(e){setStatus(e.message,'error')}}
async function openInbox(e){e=decodeURIComponent(e);try{let d=await api('/api/emails/'+encodeURIComponent(e)+'/messages');document.querySelector('#inbox').innerHTML=`<div class="card"><h2>${esc(e)}</h2>${d.data.length?d.data.map(m=>`<button class="msg" style="display:block;width:100%;text-align:left;background:white;color:#172033;border-radius:0" onclick="openMessage('${encodeURIComponent(e)}','${encodeURIComponent(m.id)}')"><b>${esc(m.subject||'(sin asunto)')}</b><div>De: ${esc(m.from_email||m.from||'')}</div><div class="muted">${esc(m.date||'')}</div><div class="muted">${esc(m.preview||'')}</div></button>`).join(''):'<p class="muted">No hay mensajes todavía.</p>'}</div>`}catch(err){setStatus(err.message,'error')}}
async function openMessage(e,id){e=decodeURIComponent(e);id=decodeURIComponent(id);try{let d=await api('/api/emails/'+encodeURIComponent(e)+'/messages/'+encodeURIComponent(id));let m=d.data;document.querySelector('#inbox').innerHTML=`<div class="card"><button onclick="openInbox('${encodeURIComponent(e)}')">← Bandeja</button><h2>${esc(m.subject||'(sin asunto)')}</h2><div>De: ${esc(m.from_email||m.from||'')}</div><div class="muted">${esc(m.date||'')}</div><hr><div class="email-body">${m.html||esc(m.content||'')}</div></div>`}catch(err){setStatus(err.message,'error')}}
async function removeMail(e){e=decodeURIComponent(e);if(!confirm('¿Eliminar '+e+'?'))return;try{await api('/api/emails/'+encodeURIComponent(e),{method:'DELETE'});loadMails();document.querySelector('#inbox').innerHTML=''}catch(err){setStatus(err.message,'error')}}
function setStatus(s,c='muted'){let x=document.querySelector('#status');x.textContent=s;x.className=c}async function mode(){try{let h=await api('/health');document.querySelector('#mode').textContent=h.tempmailg_api_configured?'Modo API oficial TempMailG':(h.emailnator_available?'Modo Gmail gratuito sin API key':'Sin proveedor disponible')}catch(e){}}mode();loadMails();
</script></body></html>'''


@app.get("/")
def index():
    return render_template_string(HTML)


def browser_agent_configured():
    import os
    return bool(os.getenv("ENABLE_BROWSER_AGENT", "True").lower() == "true" and os.getenv("MISTRAL_BROWSER_AGENT_URL"))


def configured_error():
    if TempMailGAPI().configured or browser_agent_configured():
        return None
    return "No hay proveedor configurado."


@app.get("/health")
def health():
    import os
    return jsonify({"service": "mails-docker", "status": "ok", "tempmailg_api_configured": TempMailGAPI().configured, "mailtm_available": True, "free_temp_available": True, "emailnator_available": True, "browser_agent_configured": browser_agent_configured(), "vpn_enabled": os.getenv("VPN_ENABLED", "false").lower() == "true"})


@app.get("/api/emails")
def list_api():
    return jsonify({"ok": True, "data": db_get_emails(provider=None, is_active=True)})


@app.post("/api/emails")
def create_api():
    try:
        if TempMailGAPI().configured:
            email = generate_email(provider="tempmailg")
            if not email:
                raise TempMailGAPIError("TempMailG no devolvió un correo")
            return jsonify({"ok": True, "data": {"email": email, "mode": "api"}}), 201
        # Por defecto garantizamos el requisito @gmail.com: Emailnator expone
        # sus endpoints JSON públicos y no necesita navegador ni API key.
        email = emailnator_provider.create_mailbox()
        return jsonify({"ok": True, "data": {"email": email, "mode": "gmail-free-api"}}), 201
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503


@app.get("/api/emails/<path:email>/messages")
def messages_api(email):
    try:
        info = get_email_by_email(email)
        if not info:
            return jsonify({"ok": False, "error": "Correo no encontrado"}), 404
        if info["provider"] == "emailnator":
            return jsonify({"ok": True, "data": emailnator_provider.messages(email)})
        if info["provider"] in ("tempmailportal", "smails"):
            return jsonify({"ok": True, "data": free_temp_provider.messages(email)})
        if info["provider"] == "mailtm":
            return jsonify({"ok": True, "data": mailtm_provider.messages(email)})
        if TempMailGAPI().configured:
            return jsonify({"ok": True, "data": get_emails(email, provider="tempmailg")})
        if browser_agent_configured():
            from browser_agent import read_inbox
            return jsonify({"ok": True, "data": read_inbox(email)})
        raise TempMailGAPIError("No hay proveedor disponible")
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503


@app.get("/api/emails/<path:email>/messages/<message_id>")
def message_api(email, message_id):
    try:
        info = get_email_by_email(email)
        if not info:
            return jsonify({"ok": False, "error": "Correo no encontrado"}), 404
        if info["provider"] == "emailnator":
            return jsonify({"ok": True, "data": emailnator_provider.message(email, message_id)})
        return jsonify({"ok": False, "error": "Proveedor no admite apertura individual"}), 404
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503


@app.delete("/api/emails/<path:email>")
def delete_api(email):
    try:
        info = get_email_by_email(email)
        if info and info["provider"] == "emailnator":
            return jsonify({"ok": emailnator_provider.delete(email)})
        if info and info["provider"] in ("tempmailportal", "smails"):
            return jsonify({"ok": free_temp_provider.delete(email)})
        if info and info["provider"] == "mailtm":
            return jsonify({"ok": mailtm_provider.delete(email)})
        return jsonify({"ok": delete_email(email, provider="tempmailg")})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
