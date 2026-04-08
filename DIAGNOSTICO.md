# Saulo v2 - Diagnóstico y Corrección

## Problema Identificado

El dominio `saulo.dogma.tools` mostraba texto plano en lugar de la interfaz gráfica.

## Causa Raíz

El orden de las rutas en `main.py` causaba que el endpoint de health/api respondiera en `/` en lugar de servir el `index.html`.

## Corrección Aplicada

### Cambios en `main.py`:

1. **Ruta raíz primero**: Se movió `@app.get("/")` al inicio, antes de incluir los routers
2. **Prefijo API**: Se agregó `prefix="/api"` a los routers de auth y chat
3. **Rutas de debug movidas**: Health e info ahora están en `/api/health` y `/api/info`
4. **Deshabilitados docs**: `docs_url=None` y `redoc_url=None` para producción

### Cambios clave:

```python
# ANTES (problema):
app.include_router(auth_router)  # Sin prefijo
app.include_router(chat_router)  # Rutas en /
@app.get("/")  # Demasiado tarde

# DESPUÉS (corregido):
@app.get("/", response_class=HTMLResponse)  # Primero
async def serve_index(): ...

app.include_router(auth_router, prefix="/api")  # Con prefijo
app.include_router(chat_router, prefix="/api")

@app.get("/api/health")  # Movido a /api
```

## Validación

Para verificar que funciona:

1. Iniciar servidor:
   ```
   cd C:\Users\xiute\Desktop\saulo-v2
   python -m uvicorn main:app --host 0.0.0.0 --port 8095
   ```

2. Verificar en navegador:
   - Local: http://localhost:8095
   - Público: https://saulo.dogma.tools

3. Deberías ver:
   - ✅ Interfaz con sidebar + chat (no texto plano)
   - ✅ "Hola! Soy Saulo"
   - ✅ Input de mensaje funcional

## Scripts Actualizados

- `start-saulo.bat` - Inicia servidor en puerto 8095
- `setup-cloudflare.bat` - Configura tunnel para saulo.dogma.tools

## Notas

- Puerto: 8095 (para evitar conflictos con otros servicios)
- Modelo default: gpt-oss (local)
- Admin: xiute / admin123
- Auth: JWT token almacenado en localStorage

---

*Corregido: 2026-04-08*
