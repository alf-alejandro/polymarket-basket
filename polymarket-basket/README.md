# Basket — Divergencia Armónica ETH/SOL/BTC

Bot de backtesting en vivo sobre mercados UP/DOWN 5m de Polymarket.
Sin ejecución de órdenes reales — solo simulación.

## Archivos

| Archivo | Descripción |
|---|---|
| `basket.py` | Bot principal (loop asíncrono) |
| `strategy_core.py` | Discovery de mercados + order book + señales |
| `dashboard.py` | Servidor web Flask (dashboard en tiempo real) |
| `requirements.txt` | Dependencias Python |
| `Procfile` | Comandos de proceso para Railway |

---

## Deploy en Railway — paso a paso

### 1. Subir el repo a GitHub

```bash
cd polymarket-basket
git init
git add .
git commit -m "initial deploy"
gh repo create polymarket-basket --private --push --source=.
# o:
git remote add origin https://github.com/TU_USUARIO/polymarket-basket.git
git push -u origin main
```

### 2. Crear el proyecto en Railway

1. Ir a [railway.app](https://railway.app) → **New Project**
2. **Deploy from GitHub repo** → seleccionar `polymarket-basket`
3. Railway va a detectar el `Procfile` automáticamente.

### 3. Crear DOS servicios desde el mismo repo

Railway permite múltiples servicios en un proyecto.

**Servicio 1 — Bot:**
- Settings → **Start Command**: `python basket.py`
- No necesita dominio público

**Servicio 2 — Dashboard:**
- Settings → **Start Command**: `gunicorn dashboard:app --bind 0.0.0.0:$PORT --workers 1 --threads 2`
- Settings → **Generate Domain** (para acceder por URL)

> Ambos servicios usan el mismo código del repo.

### 4. Variable de entorno compartida (crítico)

Los dos servicios deben compartir el mismo `STATE_FILE` para que el dashboard
lea el estado del bot.

**Opción A — Volumen compartido de Railway (recomendado):**
1. En el proyecto Railway → **Add Volume**
2. Montarlo en `/data` en ambos servicios
3. Agregar variable de entorno en los dos servicios:
   ```
   STATE_FILE = /data/state.json
   LOG_FILE   = /data/basket_log.json
   CSV_FILE   = /data/basket_trades.csv
   ```

**Opción B — Sin volumen (los datos se pierden al redeploy, pero funciona):**
- No configurar nada extra. El bot escribe en `/tmp/state.json` y el dashboard
  lee del mismo `/tmp`. Solo funciona si ambos servicios corren en el mismo
  contenedor (Railway puede o no garantizar esto).
- Para producción real, usar Opción A.

### 5. Verificar

- Bot: ver logs en Railway → debería mostrar `basket.py iniciado`
- Dashboard: abrir la URL generada → debería mostrar el dashboard en tiempo real

---

## Variables de entorno disponibles

| Variable | Default | Descripción |
|---|---|---|
| `STATE_FILE` | `/tmp/state.json` | Archivo de estado compartido |
| `LOG_FILE` | `/tmp/basket_log.json` | Log JSON de trades |
| `CSV_FILE` | `/tmp/basket_trades.csv` | CSV de trades |

---

## Arquitectura

```
basket.py  ──escribe──►  /data/state.json  ──lee──►  dashboard.py
   │                                                       │
   └── stdout → Railway logs                     GET /api/state (JSON)
                                                 GET /         (HTML UI)
```

El dashboard hace polling cada 1.5s a `/api/state` y actualiza la UI sin recargar.
