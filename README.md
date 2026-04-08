# Saulo v2 - Chat Interface for Langosta

Interfaz de chat moderna tipo Discord para Langosta AI.

## Características

- **Interfaz tipo Discord**: Sidebar + área de chat con glassmorphism
- **Modelo default**: gpt-oss (local via Ollama)
- **Autenticación**: JWT para acceso admin
- **Detección de intenciones**: Médico / Código / General
- **Modo Langosta**: Acceso directo a Langosta para admin

## Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/xiute/saulo-v2.git
cd saulo-v2

# 2. Crear entorno virtual
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install fastapi uvicorn python-jose pydantic httpx

# 4. Iniciar
python -m uvicorn main:app --host 0.0.0.0 --port 8095
```

## Uso

1. Abrir http://localhost:8095
2. Verás la interfaz de chat de Saulo
3. Seleccionar modelo en el sidebar
4. Escribir mensaje y presionar Enter

### Modo Admin (Langosta)

Para acceder a Langosta directamente:
1. Click en "Admin" en el sidebar
2. Login: `xiute` / `admin123`
3. Badge "Langosta Mode" aparecerá

## Estructura

```
saulo-v2/
├── main.py                 # FastAPI app con fix de rutas
├── auth/                   # JWT auth
│   ├── router.py
│   ├── dependencies.py
│   └── utils.py
├── chat/                   # Chat logic
│   ├── router.py
│   ├── service.py
│   └── models.py
├── ollama/                 # Ollama client
│   └── client.py
├── medical/                # PubMed search
│   ├── searcher.py
│   └── formatter.py
├── openclaw/               # Langosta bridge
│   └── bridge.py
├── static/                 # Frontend
│   ├── index.html
│   ├── app.js
│   └── styles.css
└── scripts/
    ├── start-saulo.bat
    ├── setup-cloudflare.bat
    └── kill-all-processes.bat
```

## Cloudflare Tunnel

Para exponer públicamente:

```bash
cloudflared tunnel create saulo
cloudflared tunnel route dns saulo saulo.dogma.tools
cloudflared tunnel run saulo
```

## Corrección Aplicada

**Problema**: El dominio mostraba texto plano en lugar de la GUI.

**Causa**: Orden incorrecto de rutas en FastAPI.

**Fix**: Ruta `/` ahora sirve `index.html` **antes** de incluir los routers.

```python
# CORREGIDO en main.py:
@app.get("/", response_class=HTMLResponse)  # ← PRIMERO
async def serve_index(): ...

app.include_router(auth_router, prefix="/api")  # ← CON PREFIJO
app.include_router(chat_router, prefix="/api")
```

## Configuración

- **Puerto**: 8095
- **Modelo default**: gpt-oss
- **Admin**: xiute / admin123
- **CORS**: Habilitado para todas las URLs

## Licencia

MIT - Para uso personal y familiar.

---

🦞 Powered by Langosta
