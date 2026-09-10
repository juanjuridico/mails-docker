from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# Configuración del WebDriver (Chrome)
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Modo sin interfaz gráfica
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    # Para Docker: Usar el ChromeDriver del sistema o descargarlo
    service = Service(executable_path=os.getenv("CHROMEDRIVER_PATH", ChromeDriverManager().install()))
    driver = webdriver.Chrome(service=service, options=options)
    return driver

TEMPMAILG_URL = "https://tempmailg.com/es"

def generate_email():
    """Genera un correo temporal en TempMailG."""
    driver = get_driver()
    driver.get(TEMPMAILG_URL)
    
    try:
        # Esperar a que cargue el correo generado (selectores comunes)
        email_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#mail, input[name='email'], .email-address, #email-input"))
        )
        email = email_element.get_attribute("value")
        if not email:
            email = email_element.text
        
        print(f"✅ Correo generado: {email}")
        return email
    except Exception as e:
        print(f"❌ Error al generar el correo: {e}")
        # Intentar con otro selector común
        try:
            email_element = driver.find_element(By.CSS_SELECTOR, "div.email, span.email, #email")
            email = email_element.text
            print(f"✅ Correo generado (selector alternativo): {email}")
            return email
        except Exception as e2:
            print(f"❌ Error con selector alternativo: {e2}")
            return None
    finally:
        driver.quit()

def get_inbox(email=None):
    """Obtiene los correos del buzón en TempMailG."""
    driver = get_driver()
    driver.get(f"{TEMPMAILG_URL}")
    
    try:
        # Esperar a que cargue el buzón
        messages = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".message, .email-item, .inbox-message, li.message"))
        )
        
        inbox = []
        for msg in messages:
            try:
                subject = msg.find_element(By.CSS_SELECTOR, ".subject, .title, .email-subject").text
            except:
                subject = "Sin asunto"
            
            try:
                sender = msg.find_element(By.CSS_SELECTOR, ".from, .sender, .email-from").text
            except:
                sender = "Desconocido"
            
            try:
                body = msg.find_element(By.CSS_SELECTOR, ".body, .content, .email-body").text
            except:
                body = ""
            
            inbox.append({
                "subject": subject,
                "from": sender,
                "body": body[:200] + "..." if len(body) > 200 else body
            })
        
        return inbox
    except Exception as e:
        print(f"❌ Error al leer el buzón: {e}")
        return []
    finally:
        driver.quit()

# Ejemplo de uso:
if __name__ == "__main__":
    print("Generando correo temporal en TempMailG...")
    email = generate_email()
    
    if email:
        print(f"\nCorreo generado: {email}")
        print("\nEsperando 15 segundos para simular recepción de correos...")
        time.sleep(15)
        
        print("\nLeyendo buzón...")
        inbox = get_inbox(email)
        print(f"\nMensajes en el buzón ({len(inbox)}):")
        for i, msg in enumerate(inbox):
            print(f"\n--- Mensaje {i+1} ---")
            print(f"De: {msg['from']}")
            print(f"Asunto: {msg['subject']}")
            print(f"Cuerpo: {msg['body']}")
