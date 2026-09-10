# 🧠 mind.md - Mapa Mental del Proyecto mails-docker

**Última actualización:** 10 de septiembre de 2026 - 20:30:00 (UTC-5)
**Objetivo:** Documentar el proceso, decisiones y estado actual del proyecto.

---

## 📌 Contexto Inicial
- **Proyecto:** mails-docker (sistema Dockerizado para generar correos temporales).
- **Requisito clave:** Los correos generados deben terminar en `@gmail.com`.
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
- **Pruebas Unitarias:** ✅ 28/28 pasadas (100%).
- **Pruebas de Integración:** ✅ 12/12 pasadas (100%).
- **Total:** ✅ 40/40 pruebas pasadas.

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
