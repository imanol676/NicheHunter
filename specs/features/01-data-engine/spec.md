# Specification: Feature 01 - Motor de Datos (Data Engine)

> **Feature**: `01-data-engine`  
> **Estado**: Especificación Aprobada / En Producción  
> **Componente**: Data Extraction, Scrapers & AI Pain Point Extraction

---

## 🎯 1. Propósito y Valor de Negocio

El **Motor de Datos** es la piedra angular de NicheHunter. Su objetivo es transformar una consulta de nicho planteada por el usuario (ej. *"Real Estate Leads"*) en una muestra amplia y representativa de publicaciones no estructuradas recolectadas de múltiples plataformas abiertas, filtrar el ruido social y extraer únicamente **fricciones B2B reales, fallos de software y cuellos de botella operativos**.

---

## 👤 2. Historias de Usuario

### HU-01: Extracción Multi-Fuente Sin Costos
> **Como** emprendedor o analista de producto,  
> **Quiero** que la plataforma escanee automáticamente Reddit, Hacker News, transcripciones de YouTube y portales B2B (G2/Capterra/Trustpilot),  
> **Para** obtener una muestra representativa de lo que se queja mi mercado objetivo sin pagar APIs costosas de scraping.

### HU-02: Filtrado Inteligente de Dolor B2B
> **Como** fundador,  
> **Quiero** que la IA descarte opiniones personales, spam y publicaciones inspiracionales,  
> **Para** trabajar únicamente con problemas cuantitativos de software o procesos que generen pérdidas de tiempo o dinero.

### HU-03: Resiliencia y Retroalimentación en Tiempo Real
> **Como** usuario del Dashboard,  
> **Quiero** ver el progreso en vivo de la extracción de publicaciones y quejas sin que la tarea colapse por límites de API o deslices de red.

---

## ✅ 3. Criterios de Aceptación (Acceptance Criteria)

| ID | Criterio de Aceptación | Método de Verificación | Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **CA-01** | La expansión de nicho genera entre 8 y 10 subreddits, keywords de HN, consultas de YT y búsquedas B2B. | Inspección de `expand_niche_to_sources` en logs. | **PASO**: Retorna diccionario con listas ampliadas de 10 elementos por canal. |
| **CA-02** | Extrae transcripciones habladas de YouTube utilizando `youtube-transcript-api`. | Ejecución de `try_fetch_youtube`. | **PASO**: Retorna registros con `source_platform = 'youtube_transcript'` y texto del video. |
| **CA-03** | El extractor de dolor no sobrepasa la cuota de 6,000 TPM de Groq y maneja respuestas 429 sin perder posts. | Ejecución de `procesar_lote_de_posts`. | **PASO**: Trunca texto a 1200 caracteres, espera 2.0s por llamada y reintenta 6s en 429 sin descartar el post. |
| **CA-04** | El worker procesa la totalidad de los RawPosts mediante un bucle por lotes en lugar de un límite rígido de 100. | Inspección de base de datos Postgres. | **PASO**: `RawPost` procesados por completo hasta dejar 0 sin analizar. |
| **CA-05** | Si los dolorosos extraídos válidos son `< 3`, el escaneo se marca como `"failed_no_data"` limpiamente. | Consulta a tabla `scan_jobs`. | **PASO**: `phase = 'failed_no_data'` sin excepciones en Celery. |
