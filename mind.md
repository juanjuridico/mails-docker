# 🧠 mind.md - Mapa Mental del Proyecto mails-docker

> **Antes de seguir**: leé `/workspace/mind.md` — ahí está documentada la infraestructura compartida (mcp-bash, Docker, git/GitHub, Traefik, DNS vía `domains-docker`, credenciales) que usan TODOS los proyectos de este servidor, con los gotchas ya pisados por sesiones anteriores. Si descubrís algo nuevo sobre esa infraestructura (no específico de este proyecto), agregalo ahí, no acá.


**Última actualización:** 11 de septiembre de 2026 - 17:30:00 (UTC-5)
**Objetivo:** Documentar el proceso, decisiones y estado actual del proyecto.

---

## 📌 Contexto Inicial
- **Proyecto:** mails-docker (sistema Dockerizado para generar correos temporales).
- **Requisito clave:** Los correos generados deben terminar en `@gmail.com`.
- **Estado:** proyecto funcional y desplegado; CLI disponible mediante `docker exec`.
- **Bloqueo externo actual:** TempMailG `/gmail-temp-mail` devuelve Cloudflare Turnstile al servidor; generación real no puede completarse sin una vía autorizada/API key.
- **Herramientas:** TempMailG (https://tempmailg.com/es) + Selenium.

---

## 📁 Estructura del Proyecto
```
mails-docker/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── cli.py
├── db.py
├── email_service.py
├── tempmailg_service.py
├── selenium_utils.py
├── mind.md
├── constitucion.md
├── specs.md
├── tasks.md
├── agents.md
├── tests/
│   ├── __init__.py
│   ├── test_selenium_utils.py
│   ├── test_tempmailg_service.py
│   ├── test_db.py
│   ├── test_email_service.py
│   ├── test_cli.py
│   └── test_integration.py
├── data/
├── logs/
└── screenshots/
```

---

## 🧪 Resultados de Pruebas (10/09/2026)
- **Pruebas automatizadas actuales:** ✅ 11/11 pasadas (100%).
- **Smoke test Selenium real:** ✅ Chromium + ChromeDriver contra `https://example.com`.
- **Imagen Docker:** ✅ construida y probada en la arquitectura del servidor.

---

## 🚀 Despliegue
1. Ejecutar: `chmod +x deploy_to_production.sh && ./deploy_to_production.sh`
2. Verificar: `docker ps` y `docker exec -it mails-docker-app python cli.py list`

---

## 📥 Subida a GitHub
- Repositorio: https://github.com/juanjuridico/mails-docker
- Ejecutar: `chmod +x push_to_github.sh && ./push_to_github.sh`

---

## 📌 Notas
- Selectores de TempMailG pueden cambiar. Validar periódicamente.
- Usar proxies en producción para evitar bloqueos.
- Preinstalar ChromeDriver en entornos sin internet.
