# 📋 specs.md - Especificaciones Técnicas

**Proyecto:** mails-docker
**Objetivo:** Detallar requisitos, arquitectura y módulos.

---

## 🎯 Requisitos Funcionales

### 1. Generación de Correos
- **Requisito:** Generar correos temporales que terminen en `@gmail.com`.
- **Proveedor:** TempMailG (https://tempmailg.com/es) + Selenium.
- **Alternativas:** Gmailnator/TempMail como fallback.

### 2. Gestión de Correos
- Generar N correos.
- Listar correos activos.
- Leer correos recibidos.
- Eliminar correos.
- Sincronizar correos.

### 3. Persistencia
- **Base de datos:** SQLite (`emails.db`).
- **Campos:** id, email, provider, domain, created_at, expires_at, is_active.

---

## 🏗️ Arquitectura

### Módulos Principales
| Módulo | Responsabilidad | Dependencias |
|--------|-----------------|---------------|
| `cli.py` | Interfaz de línea de comandos | argparse, email_service.py |
| `email_service.py` | Lógica principal | tempmailg_service.py, db.py |
| `tempmailg_service.py` | Interacción con TempMailG | selenium_utils.py, webdriver-manager |
| `selenium_utils.py` | Utilidades para Selenium | selenium |
| `db.py` | Base de datos SQLite | sqlite3 |

### Flujo de Trabajo
1. CLI → email_service.py → tempmailg_service.py → Selenium → TempMailG.
2. Los correos se guardan en `emails.db` mediante `db.py`.

---

## 🔧 Especificaciones por Módulo

### tempmailg_service.py
- **Funciones:** generate_email(), get_emails(), delete_email(), sync_emails().
- **Flujo:** Abrir navegador → Navegar a TempMailG → Extraer correo → Validar dominio `@gmail.com` → Guardar en DB.

### selenium_utils.py
- **Funciones:** init_driver(), close_driver(), wait_for_element(), take_screenshot(), random_delay().
- **Configuración:** Chrome en modo headless, ChromeDriver automático.

### db.py
- **Tabla emails:** id (PK), email (UNIQUE), provider, domain, created_at, expires_at, is_active.
- **Funciones:** init_db(), add_email(), get_emails(), delete_email(), mark_as_inactive().

---

## 📦 Dependencias

### Python (requirements.txt)
```
selenium==4.15.0
webdriver-manager==4.0.1
sqlite3==3.41.2
argparse==1.4.0
python-dotenv==1.0.0
pytest==8.0.0
```

### Docker (Dockerfile)
- Imagen base: python:3.11-slim
- Chrome + ChromeDriver para Selenium.

---

## 🌐 Integración con TempMailG
- **URL:** https://tempmailg.com/es
- **Selectores:** `//*[@id="email"]` (correo), `//*[@class="message"]` (correos recibidos).
- **Notas:** Validar selectores periódicamente.
