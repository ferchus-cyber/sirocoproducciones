# Siroco Producciones — Web

## Problem Statement
Web dinámica estilo flamenco para Siroco Producciones (producción de espectáculos musicales, San Fernando, Cádiz). Requisitos: botón multiidioma (ES/EN/DE/FR), contenido dinámico en base de datos, panel admin con login, formulario de contacto que guarda en BD, colores blanco/negro/rojo, logo principal grande, enlace Instagram, sección "Origen del Nombre Siroco". Traducción con IA.

## Architecture
- Frontend: React (CRA + Tailwind + shadcn), framer-motion. Rutas: `/` (Home), `/admin`.
- Backend: FastAPI + MongoDB (motor). Auth JWT Bearer (localStorage `siroco_token`).
- Traducción: emergentintegrations (gemini-3-flash-preview), cache en colección `translations`.
- Imágenes servidas desde `/frontend/public/media`.

## Implemented (2026-07-01)
- Home con secciones: Hero (logo grande), Servicios, Nosotros, Origen del Nombre, Artistas, Contacto, Footer.
- Orden actualizado: Artistas es la antepenúltima sección (Artistas → Contacto → Footer).
- Logo del usuario (imagen subida) usado en header, hero y footer.
- Selector de idioma ES/EN/DE/FR con traducción IA + cache (fallback a ES si no hay saldo LLM).
- 8 artistas (Diego Carrasco y "Voces con las que hemos caminado" excluidos).
- Instagram link exacto; sin "Desde 1993"; colores blanco/negro/rojo.
- Formulario de contacto → guarda en MongoDB.
- Panel admin (/admin): login, CRUD artistas, edición de textos, ver/borrar mensajes.
- Testeado E2E: backend 14/14, frontend flujos críticos OK.

## Credentials
Admin: admin@sirocoproducciones.com / Siroco2026! (ver test_credentials.md)

## Backlog / Next
- P1: Recarga saldo Universal Key para activar traducciones reales (actualmente cae a ES si saldo 0).
- P2: Subida de imágenes de artistas desde el admin (object storage) en vez de URL manual.
- P2: SEO/meta tags y favicon con el nuevo logo.
