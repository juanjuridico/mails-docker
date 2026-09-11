"""Cliente del agente de navegador alojado en mistral-docker."""
import os
import re
import requests

class BrowserAgentError(RuntimeError):
    pass

BASE=os.getenv('MISTRAL_BROWSER_AGENT_URL','http://mistral_backend:6011/api/browser-agent').rstrip('/')
TIMEOUT=int(os.getenv('MISTRAL_BROWSER_AGENT_TIMEOUT','180'))


def run(task:str,max_steps:int=12):
    try:
        r=requests.post(BASE,json={'task':task,'max_steps':max_steps},timeout=TIMEOUT)
    except requests.RequestException as exc:
        raise BrowserAgentError(f'No se pudo contactar mistral-docker: {exc}') from exc
    try: data=r.json()
    except ValueError: raise BrowserAgentError(f'mistral-docker respondió HTTP {r.status_code}')
    if r.status_code >= 400:
        raise BrowserAgentError(data.get('detalle') or data.get('error') or str(data))
    return data


def extract_email(data):
    text=' '.join([
        str(data.get('message','')),
        str(data.get('ocr','')),
        str(data.get('history','')),
    ])
    matches=re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',text)
    return matches[0] if matches else None
