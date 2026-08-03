# Constitución del Proyecto NicheHunter (System Constitution)

> **Versión**: 1.0.0  
> **Estado**: Aprobado / Inmutable  
> **Metodología**: Spec-Driven Development (GitHub Spec Kit)

Esta Constitución establece los principios fundamentales, restricciones arquitectónicas y reglas de gobernanza técnica para el desarrollo de **NicheHunter** como plataforma de Inteligencia de Mercado B2B. Todo desarrollador o agente de IA debe cumplir rigurosamente estas reglas.

---

## 🏛️ Principios Fundamentales Inmutables

### 1. Veracidad de Datos Cuantitativos (Cero Alucinaciones en TAM/CAGR)
- **Regla**: Queda estrictamente prohibido ordenar o permitir que los modelos de lenguaje (LLMs) inventen o estimen con asterisco cifras financieras (TAM o CAGR) si no existen evidencias verificables en búsquedas web abiertas.
- **Acción ante falta de datos**: Se debe retornar explícitamente `"Unverified in open sources"` para TAM y `"N/A"` para CAGR. La credibilidad del producto es la máxima prioridad.

### 2. Infraestructura de Scraping 100% Gratuita
- **Regla**: El motor de datos debe depender exclusivamente de métodos y APIs abiertas 100% gratuitas (`duckduckgo_search`, `youtube-transcript-api`, API pública de Algolia HN, JSON endpoints públicos de Reddit).
- **Acción ante fallos**: Implementar rotación dinámica de User-Agents, paginación inteligente y retroceso exponencial (*exponential backoff*) ante respuestas HTTP 429/403. No se integrarán APIs de pago de terceros para scraping en las fases base.

### 3. Resiliencia de Concurrencia & Sockets (Windows & Docker)
- **Regla**: Celery debe ejecutarse con `--pool=solo` en entornos Windows (`os.name == 'nt'`) para evitar la corrupción de sockets entre procesos (`WinError 10054`).
- **Control de Event Loops**: Ninguna tarea asíncrona de Celery debe cerrar el bucle de eventos sin antes liberar o limpiar el pool de conexiones de SQLAlchemy (`await engine.dispose()`) con `pool_pre_ping=True`.
- **Actualización Segura de Estado**: Toda llamada a `update_state` en Celery debe estar resguardada para capturar micro-cortes de Redis sin abortar la ejecución del escaneo.

### 4. Control Estricto de Rate Limits (Groq 6,000 TPM)
- **Regla**: Toda interacción con la API de Groq (`llama-3.1-8b-instant`) debe estar limitada en tamaño de entrada (máximo 1,200 caracteres / ~250 tokens por post) y espaciada con pausas intencionales de mínimo 2.0 segundos entre llamadas.
- **Manejo de HTTP 429**: En caso de error de límite de velocidad (Rate Limit), el sistema **NUNCA descartará la publicación**. Implementará un bucle de reintento automático con esperas de 6.0 segundos.

### 5. Contratos de Datos Rigurosos y Fuertemente Tipados
- **Regla**: Toda la comunicación entre Backend (FastAPI), Workers (Celery) y Frontend (Next.js) debe estar tipada con esquemas Pydantic / TypeScript explicitados en sus respectivos `plan.md`. Queda prohibido el uso de tipos `any` o datos JSON impredecibles.

---

## 🔄 Flujo de Trabajo Spec Kit (SDD Workflow)

Cualquier nueva característica o modificación debe seguir la secuencia obligatoria:

1. **`specs/features/XX-feature/spec.md`**: Definición funcional, Historias de Usuario y Criterios de Aceptación.
2. **`specs/features/XX-feature/plan.md`**: Diseño técnico, diagramas de arquitectura, esquemas DB y endpoints API.
3. **`specs/features/XX-feature/tasks.md`**: Lista atómica de tareas de desarrollo.
4. **Implementación & Verificación**: Desarrollo del código y validación automatizada contra los criterios de aceptación.
