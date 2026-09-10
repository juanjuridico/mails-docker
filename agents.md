# 🤖 agents.md - Agentes y Automatización

**Proyecto:** mails-docker
**Objetivo:** Documentar automatización con Selenium y TempMailG.

---

## 🎯 Introducción
Este documento describe la automatización en el proyecto:
1. **Selenium:** Automatización del navegador.
2. **TempMailG:** Sitio web para correos temporales.

---

## 🔧 Selenium

### Configuración Básica
- **Navegador:** Chrome (modo headless).
- **Driver:** ChromeDriver (gestionado con webdriver-manager).
- **Dependencias:** selenium==4.15.0, webdriver-manager==4.0.1.

### Utilidades (selenium_utils.py)
- **init_driver():** Inicializa WebDriver de Chrome.
- **close_driver():** Cierra el navegador.
- **wait_for_element():** Espera a que un elemento esté presente.
- **random_delay():** Retrasos aleatorios para evitar detección como bot.

### Buenas Prácticas
- Usar `time.sleep(random.uniform(0.5, 2.0))` entre acciones.
- User-Agent personalizado para evitar bloqueos.
- Cerrar el navegador siempre con `try/finally`.

---

## 🌐 TempMailG

### URL Base
```python
TEMPMAILG_URL = "https://tempmailg.com/es"
```

### Flujo de Generación de Correos
1. Abrir navegador con Selenium.
2. Navegar a TempMailG.
3. Esperar a que se genere el correo (selector: `//*[@id="email"]`).
4. Validar que el correo termine en `@gmail.com`.
5. Almacenar en `emails.db` con `db.py`.
6. Cerrar el navegador.

### Selectores de TempMailG
| Elemento | Selector (XPath) |
|----------|------------------|
| Correo generado | `//*[@id="email"]` |
| Lista de correos | `//*[@class="message"]` |
| Remitente | `.//*[@class="sender"]` |
| Asunto | `.//*[@class="subject"]` |

> **Nota:** Los selectores pueden cambiar. Validarlos antes de usar.

---

## 🔄 Integración con el Proyecto
- **tempmailg_service.py:** Usa `selenium_utils.py` para manejar el navegador.
- **email_service.py:** Integra `tempmailg_service.py` como proveedor.
- **cli.py:** Permite seleccionar el proveedor con `--provider tempmailg`.

---

## ⚠️ Posibles Problemas y Soluciones
| Problema | Causa | Solución |
|---------|-------|----------|
| Correo no termina en @gmail.com | TempMailG generó otro dominio | Repetir el proceso o usar otro proveedor |
| Selenium no encuentra elemento | Selector incorrecto | Validar selectores en agents.md |
| TempMailG bloquea solicitudes | Detección como bot | Usar `random_delay()` y rotar User-Agent |
| ChromeDriver no se instala | Problemas de red | Preinstalar ChromeDriver en Dockerfile |
