# Tasks: Feature 01 - Motor de Datos (Data Engine)

> **Feature**: `01-data-engine`  
> **Estado**: Tareas Verificadas y Completadas en Producción  
> **Seguimiento**: Spec Kit Implementation Checklist

---

## 📝 Lista de Tareas Atómicas de Implementación

- [x] **Task 01-01**: Configurar expansión de fuentes a 10 elementos por canal en `backend/src/services/ai/niche_expander.py`.
- [x] **Task 01-02**: Implementar cliente de transcripciones habladas de YouTube (`youtube-transcript-api`) en `backend/src/services/scraper/youtube_api_client.py` con fallback abierto.
- [x] **Task 01-03**: Ampliar scraper B2B abierto a G2, Capterra, Trustpilot, ProductHunt y LinkedIn Posts en `backend/src/services/scraper/b2b_search_client.py`.
- [x] **Task 01-04**: Implementar paginación de 3 niveles en Hacker News Algolia API en `backend/src/services/scraper/hn_json_client.py`.
- [x] **Task 01-05**: Implementar procesamiento por lotes iterativo (*chunks* de 25) sin límite de 100 posts en `backend/src/services/ai/pain_point_extractor.py`.
- [x] **Task 01-06**: Añadir control de tokens (1,200 chars max), reintentos con pausa de 6s en 429 y espaciado de 2.0s por post en `backend/src/services/ai/pain_point_extractor.py`.
- [x] **Task 01-07**: Configurar `worker_pool = 'solo'` en `backend/src/workers/celery_app.py` para compatibilidad total con Windows sin corrupción de sockets.
- [x] **Task 01-08**: Crear helper `safe_update_state` y `run_async` con `await engine.dispose()` en `backend/src/workers/tasks.py` para prevenir `RuntimeError: Event loop is closed`.
- [x] **Task 01-09**: Configurar `pool_pre_ping = True` y `pool_recycle = 300` en `backend/src/db/engine.py`.
- [x] **Task 01-10**: Integrar callback de progreso dinámico en `procesar_lote_de_posts` para actualizar la interfaz web en tiempo real por cada lote de 25 publicaciones.
