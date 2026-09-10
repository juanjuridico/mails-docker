# 📜 constitucion.md - Constitución del Proyecto mails-docker

**Proyecto:** mails-docker
**Objetivo:** Establecer reglas, principios y convenciones.

---

## 🏛️ Principios Fundamentales

### 1. Enfoque en el Usuario
- Priorizar usabilidad y experiencia del desarrollador.
- Los correos deben ser funcionales y terminar en `@gmail.com`.

### 2. Calidad del Código
- Legibilidad: Código fácil de entender y mantener.
- Modularidad: Cada componente tiene una responsabilidad única.
- Reutilización: Evitar duplicación de código.

### 3. Transparencia y Documentación
- Todo cambio o decisión debe documentarse en `mind.md`.
- Mantener actualizados: `mind.md`, `constitucion.md`, `specs.md`, `tasks.md`.

### 4. Seguridad
- No almacenar credenciales en el repositorio.
- Validar y sanitizar entradas de usuario.
- Usar HTTPS para conexiones externas.

---

## 📜 Reglas del Proyecto

### Desarrollo
- **Branches:** Usar `main` para código estable. Crear branches temáticas (ej: `feature/tempmailg`).
- **Commits:** Mensajes descriptivos en español (ej: "Añade soporte para TempMailG").
- **Revisión:** Todo Pull Request debe ser revisado.

### Convenciones de Código
- **Python:** Seguir PEP 8, usar `snake_case` para variables/funciones, `PascalCase` para clases.
- **Docker:** Nombres de servicios en minúsculas (ej: `mails-app`).
- **Markdown:** Usar encabezados con `#`, listas con `-`.

---

## ❌ Prohibiciones
- Hardcodear credenciales.
- Ignorar errores (ej: no manejar excepciones de Selenium).
- Dejar código comentado innecesario.
- Usar dependencias no documentadas.
