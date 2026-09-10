import requests
from bs4 import BeautifulSoup
import time
import re

TEMPMAILG_URL = "https://tempmailg.com/es"

# Headers más realistas para evitar bloqueo
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
}

# Sesión persistente para mantener cookies
session = requests.Session()

def get_page(url, retry=True):
    """Obtiene el contenido de una página con la sesión actual."""
    try:
        response = session.get(url, headers=HEADERS, timeout=20)
        if response.status_code == 403:
            # Intentar con un referer diferente
            HEADERS['Referer'] = "https://tempmailg.com/"
            if retry:
                return get_page(url, retry=False)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error al obtener {url}: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response: {e.response.text[:200]}")
        return None

def generate_email():
    """Genera un correo temporal en TempMailG."""
    html = get_page(TEMPMAILG_URL)
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Buscar el correo en elementos comunes
    # Intentar con input de email
    email_element = soup.find('input', {'type': 'email'})
    if email_element and email_element.get('value'):
        return email_element.get('value')
    
    # Buscar en input con id que contenga mail
    email_element = soup.find('input', id=lambda x: x and 'mail' in x.lower())
    if email_element and email_element.get('value'):
        return email_element.get('value')
    
    # Buscar en divs o spans con clase que contenga email
    email_element = soup.find(['div', 'span', 'p'], class_=lambda x: x and 'email' in x.lower())
    if email_element:
        email = email_element.get_text(strip=True)
        if re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return email
    
    # Buscar en el title
    title = soup.title.string if soup.title else ""
    if re.match(r'[^@]+@[^@]+\.[^@]+', title):
        return title
    
    # Buscar en cualquier texto de la página
    for text in soup.stripped_strings:
        if re.match(r'[^@]+@[^@]+\.[^@]+\.com$', text):
            return text
        if re.match(r'[^@]+@gmail\.com$', text):
            return text
    
    # Imprimir el HTML para depuración
    print("\n--- HTML Recibido (primeros 1000 caracteres) ---")
    print(html[:1000])
    print("--- Fin HTML ---\n")
    
    print("❌ No se encontró el correo en la página.")
    return None

def get_inbox():
    """Obtiene los correos del buzón en TempMailG."""
    html = get_page(TEMPMAILG_URL)
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    messages = []
    
    # Buscar mensajes en elementos comunes
    message_elements = soup.find_all(['div', 'li', 'tr'], class_=lambda x: x and any(
        keyword in x.lower() for keyword in ['message', 'email', 'inbox', 'mail', 'mensaje', 'correo']
    ))
    
    for msg in message_elements:
        try:
            subject = msg.find(class_=lambda x: x and 'subject' in x.lower()).get_text(strip=True)
        except:
            subject = "Sin asunto"
        
        try:
            sender = msg.find(class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['from', 'sender', 'remitente', 'de']
            )).get_text(strip=True)
        except:
            sender = "Desconocido"
        
        try:
            body = msg.find(class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['body', 'content', 'cuerpo', 'mensaje']
            )).get_text(strip=True)
        except:
            body = ""
        
        if subject or sender or body:
            messages.append({
                "subject": subject,
                "from": sender,
                "body": body[:200] + "..." if len(body) > 200 else body
            })
    
    return messages

# Ejemplo de uso:
if __name__ == "__main__":
    print("Generando correo temporal en TempMailG...")
    email = generate_email()
    
    if email:
        print(f"\n✅ Correo generado: {email}")
        print("\nEsperando 15 segundos para simular recepción de correos...")
        time.sleep(15)
        
        print("\nLeyendo buzón...")
        inbox = get_inbox()
        print(f"\nMensajes en el buzón ({len(inbox)}):")
        for i, msg in enumerate(inbox):
            print(f"\n--- Mensaje {i+1} ---")
            print(f"De: {msg['from']}")
            print(f"Asunto: {msg['subject']}")
            print(f"Cuerpo: {msg['body']}")
    else:
        print("❌ No se pudo generar el correo.")
