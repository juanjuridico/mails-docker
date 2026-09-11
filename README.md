# 📧 mails-docker

Un sistema **Dockerizado** para generar y gestionar correos electrónicos temporales con dominio **`@gmail.com`** usando **TempMailG + Selenium**.

---

## 🌟 Características

- ✅ Generación de **correos temporales con dominio `@gmail.com`**.
- ✅ **Persistencia** de correos en base de datos SQLite.
- ✅ **Interfaz de línea de comandos (CLI)** con múltiples comandos.
- ✅ **Dockerizado** para fácil despliegue.
- ✅ **Pruebas automatizadas** (11 pruebas, 100% éxito).
- ✅ **Documentación completa** (mind.md, specs.md, tasks.md, etc.).

---

## 📋 Requisitos

- Docker
- Docker Compose
- Conexión a internet (para acceder a TempMailG)

---

## 🚀 Instalación y Uso

### 1. Clonar el repositorio
```bash
git clone https://github.com/juanjuridico/mails-docker.git
cd mails-docker
```

### 2. Configurar variables de entorno (opcional)
```bash
cp .env.example .env
nano .env
```

### 3. Construir y levantar los contenedores
```bash
docker compose build
docker compose up -d
```

### 4. Usar la CLI
```bash
docker exec -it mails-docker-app python cli.py --help
```

#### Comandos disponibles:
| Comando | Descripción |
|---------|-------------|
| `generate` | Genera un correo temporal. |
| `generate --count N` | Genera N correos temporales. |
| `list` | Lista todos los correos activos. |
| `read <email>` | Lee los correos de una dirección. |
| `delete <email>` | Elimina un correo de la base de datos. |
| `sync` | Sincroniza todos los correos activos. |

#### Ejemplos:
```bash
# Generar un correo
docker exec -it mails-docker-app python cli.py generate

# Generar 5 correos
docker exec -it mails-docker-app python cli.py generate --count 5

# Listar correos
docker exec -it mails-docker-app python cli.py list

# Leer correos de una dirección
docker exec -it mails-docker-app python cli.py read usuario123@gmail.com

# Eliminar un correo
docker exec -it mails-docker-app python cli.py delete usuario123@gmail.com
```

---

## 📂 Estructura del Proyecto
```
mails-docker/
├── Dockerfile                      # Configuración del contenedor
├── docker-compose.yml              # Orquestación de contenedores
├── requirements.txt                # Dependencias de Python
├── .env.example                    # Plantilla de variables de entorno
├── .gitignore                      # Archivos a ignorar en Git
├── cli.py                          # Interfaz de línea de comandos
├── db.py                           # Módulo de base de datos
├── email_service.py               # Servicio principal de correos
├── tempmailg_service.py            # Servicio para TempMailG
├── selenium_utils.py               # Utilidades para Selenium
├── README.md                       # Este archivo
├── mind.md                         # Mapa mental del proyecto
├── constitucion.md                 # Constitución del proyecto
├── specs.md                        # Especificaciones técnicas
├── tasks.md                        # Tareas del proyecto
├── agents.md                       # Documentación de automatización
├── tests/                          # Pruebas automatizadas
│   ├── test_selenium_utils.py
│   ├── test_tempmailg_service.py
│   ├── test_db.py
│   ├── test_email_service.py
│   ├── test_cli.py
│   └── test_integration.py
├── deploy_to_production.sh         # Script para despliegue
└── push_to_github.sh               # Script para subir a GitHub
```

---

## 🔧 Configuración

Puedes modificar las siguientes variables de entorno en el archivo `.env`:
```env
# Configuración de TempMailG
TEMPMAILG_URL=https://tempmailg.com/es

# Configuración de Selenium
CHROME_DRIVER_PATH=/usr/local/bin/chromedriver
HEADLESS_MODE=True

# Configuración de la base de datos
DB_PATH=/app/data/emails.db
```

---

## 🧪 Estado verificado

- 11 pruebas automatizadas: **11/11 pasadas**.
- Imagen Docker construida correctamente en la arquitectura del servidor.
- Chromium + ChromeDriver se instalan desde los paquetes Debian compatibles con ARM64/AMD64.
- Smoke test real de Selenium contra `https://example.com`: correcto.
- El contenedor permanece activo y la CLI se ejecuta mediante `docker exec`.

## ⚠️ Dependencia externa: TempMailG

La generación real fue probada el 11/09/2026. TempMailG actualmente protege
`/gmail-temp-mail` con Cloudflare Turnstile desde este servidor, por lo que
Selenium recibe una página `Just a moment...` y no puede obtener el alias.
El código conserva manejo de reintentos/capturas y devuelve un fallo limpio;
no se simula una dirección inexistente.

TempMailG también documenta actualmente una API de usuario que requiere una
API key y un host dedicado. Si se dispone de una key, conviene implementar el
provider API como backend preferente y dejar Selenium como fallback.

## 📌 Notas

- **TempMailG** es un servicio gratuito con límites de uso. Si el sitio falla o bloquea solicitudes, el sistema puede requerir ajustes (ej: proxies, retrasos aleatorios).
- Los correos generados son **temporales** y pueden ser eliminados por TempMailG después de cierto tiempo.
- La base de datos **SQLite** persiste los correos generados y los mensajes recibidos.
- Este proyecto está diseñado para **uso local o de desarrollo**. Para producción, se recomienda:
  - Usar proxies para evitar bloqueos.
  - Implementar backups de la base de datos.
  - Monitorear los logs.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Abre un *issue* o envía un *pull request* para mejorar el proyecto.

---

## 📜 Licencia

Este proyecto está bajo la **MIT License**. Ver [LICENSE](LICENSE) para más detalles.
