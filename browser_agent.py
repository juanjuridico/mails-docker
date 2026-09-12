"""Cliente del agente Mistral -> browser-docker para TempMailG."""
import os, re, requests

URL=os.getenv("MISTRAL_BROWSER_AGENT_URL","http://mistral_backend:6011/api/browser-agent")
TIMEOUT=float(os.getenv("MISTRAL_BROWSER_AGENT_TIMEOUT","180"))

def _run(task):
    r=requests.post(URL,json={"task":task},timeout=TIMEOUT)
    r.raise_for_status(); d=r.json()
    if not d.get("ok", True): raise RuntimeError(d.get("error","browser agent error"))
    return d

def create_mailbox():
    d=_run("""En TempMailG crea un correo temporal. Usa Chromium gráfico real y las herramientas xdotool del browser-docker. Observa la pantalla después de cada acción. Si aparece una verificación de Cloudflare, deja que el navegador ejecute JavaScript normalmente y espera; no intentes evadir, resolver ni falsificar la verificación. Continúa automáticamente si la página la supera. Cuando la página de TempMailG muestre la dirección de correo, devuélvela en tu respuesta con el formato EMAIL: direccion@dominio. Si no puedes obtenerla, explica el estado final.""")
    text=str(d)
    m=re.search(r'EMAIL:\s*([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})',text,re.I)
    if not m:
        lower=text.lower()
        if "verify you are human" in lower or "cloudflare" in lower or "security verification" in lower:
            raise RuntimeError("TempMailG está solicitando una verificación humana de Cloudflare. El navegador quedó en la página de verificación; no se intenta evadirla automáticamente.")
        raise RuntimeError("El agente no devolvió una dirección. Resultado: "+text[-1200:])
    return m.group(1)

def read_inbox(email):
    d=_run(f"""En TempMailG abre la bandeja del correo {email}. Reutiliza las coordenadas guardadas en browser-docker si existen. Observa la pantalla y navega con Chromium/x-dotool. Devuelve los mensajes visibles en JSON si es posible; si no hay mensajes devuelve una lista vacía. No uses ni inventes datos.""")
    return d.get("messages",[]) if isinstance(d,dict) else []
