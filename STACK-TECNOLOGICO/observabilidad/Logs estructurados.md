---
titulo: "Logs estructurados"
categoria:
  - "14. Observabilidad"
tags:
  - "mapa-tecnologico"
  - "nivel-dominar"
  - "observabilidad"
  - "guia-completa"
nivel: dominar
estrella: true
tipo: guia
estado: completa
actualizado: 2026-11-24
relacionado_con:
  - "[[OpenTelemetry]]"
  - "[[CloudWatch]]"
  - "[[Middleware]]"
  - "[[Correlation ID - Request ID]]"
  - "[[Formato JSON de logs]]"
  - "[[Instrumentación en middleware]]"
  - "[[Log de request-response + latencia]]"
  - "[[Logger por módulo]]"
  - "[[Logs de negocio vs técnicos]]"
  - "[[Niveles de log (DEBUG-INFO-WARN-ERROR)]]"
  - "[[Python logging - Loguru - structlog]]"
  - "[[Redacción de PII y secretos]]"
  - "[[Sampling de logs]]"
---

# Logs estructurados — Guía completa 📝

> ⭐ Núcleo imprescindible. Objetivo: que tus logs puedan ser **consultados, correlacionados y confiables**, no solo leídos con `tail -f`.

## 1. Mentalidad: qué es (y qué NO es)

Un log estructurado es un **evento con campos tipados**, emitido como JSON. La máquina es el lector principal; el humano, el secundario.

```text
Texto:       2026-11-24 10:15:02 ERROR pago rechazado para user 42 con tarjeta 4111...
Struct:      {"ts":"2026-11-24T10:15:02.131Z","level":"error","event":"pago.rechazado",
               "user_id":42,"motivo":"fondos","request_id":"c8e1...","duration_ms":12}
```

No es:

- **Un `print()` con interpolate**: pierde tipos, no se filtra y se rompe con cualquier cambio de formato.
- **Un sustituto de métricas o trazas**: los logs dicen *qué pasó*; las métricas, *cuántos*; [[OpenTelemetry]], *por dónde viajó*. Se complementan.
- **Un volcado de datos**: loggear el body completo filtra PII y llena el disco ([[Redacción de PII y secretos]]).
- **Algo que se decide después**: el [[Formato JSON de logs]] y los campos obligatorios se definen al empezar.

| Principio | En la práctica |
|---|---|
| Un evento = una línea JSON | JSONL: una línea, un `json.loads` |
| Campos estables | `ts`, `level`, `event`, `service`, `request_id` siempre igual |
| Valores tipados | Números como números, no strings |
| Contexto propagado | [[Correlation ID - Request ID]] de extremo a extremo |
| Baja cardinalidad | IDs en campos, nunca en el nombre del evento |
| Salida por stdout | [[stdout → CloudWatch - Loki]] recoge el log |
| Niveles con sentido | [[Niveles de log (DEBUG-INFO-WARN-ERROR)]] no es decoración |

> Frase para entrevista: *"Un log estructurado es un evento inmutable con esquema estable, ID de correlación y campos consultables; se emite por stdout y se agrega en el colector"*.

[[Logs estructurados]] nacen con [[Python logging - Loguru - structlog]], se instrumentan en [[Middleware]] y terminan en [[CloudWatch]] u [[OpenTelemetry]].

---

## 2. Instalación y primeros pasos

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install structlog python-json-logger
sudo apt install -y jq                # Fedora: dnf install jq | macOS: brew install jq
python -c "import logging, structlog; print(logging.__name__, structlog.__version__)"
jq --version
```

Logger mínimo con `logging` puro (JSON válido, una línea por evento):

```python
import json, logging, sys
from datetime import datetime, timezone

class JsonFormatter(logging.Formatter):
    def format(self, r: logging.LogRecord) -> str:
        d = {
            "ts": datetime.fromtimestamp(r.created, timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "level": r.levelname.lower(),
            "logger": r.name,
            "event": r.getMessage(),
        }
        for k in ("request_id", "user_id", "event_name", "duration_ms", "status_code"):
            v = getattr(r, k, None)
            if v is not None:
                d[k] = v
        if r.exc_info:
            d["exception"] = self.formatException(r.exc_info)
        return json.dumps(d, ensure_ascii=False, separators=(",", ":"))

h = logging.StreamHandler(sys.stdout)
h.setFormatter(JsonFormatter())
log = logging.getLogger("mi-app")
log.setLevel(logging.INFO)
log.addHandler(h)
log.propagate = False
log.info("servicio.iniciado", extra={"event_name": "startup"})
```

Alternativas rápidas:

```python
# structlog: recomendado para servicios con contexto por request
import structlog, logging, sys
logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)
structlog.get_logger("mi-app").info("pago.creado", pago_id="p_123", importe=1999)
```

[[Python logging - Loguru - structlog]] resume las opciones: `logging` para librerías, `structlog` para servicios, `Loguru` para scripts donde querés comodidad.

---

## 3. Cheat sheet

| Campo | Tipo | Ejemplo | Regla |
|---|---|---|---|
| `ts` | string ISO-8601 UTC | `2026-11-24T10:15:02.131Z` | Siempre UTC, milisegundos |
| `level` | string | `info`, `warn`, `error` | Minúsculas |
| `event` | string | `pago.rechazado` | `dominio.accion`, estable |
| `message` | string | `Pago rechazado por fondos` | Legible, no identificador |
| `service` / `env` / `version` | string | `pagos-api`, `prod`, `1.4.2` | Baja cardinalidad |
| `request_id` / `trace_id` | string | `c8e1-...` | Un ID por request |
| `user_id` | number/string | `42` | Nunca email ni documento |
| `duration_ms` / `status_code` | number | `12`, `503` | Números reales |
| `exception` | string | traceback escapado | Solo en `error`/`critical` |

| API | Uso |
|---|---|
| `logging.getLogger(__name__)` | [[Logger por módulo]]: jerarquía por paquete |
| `log.debug/info/warning/error(...)` | Emite según nivel |
| `log.exception("falló")` | `error` + traceback |
| `log.info("x", extra={"k": v})` | Campos estructurados |
| `logging.config.dictConfig(CFG)` | Config declarativa de producción |
| `log.addFilter(f)` | Enriquece o redacta antes de formatear |
| `formatter.formatException(exc_info)` | Traceback a string |
| `QueueHandler` / `QueueListener` | Emisión asíncrona |

| `jq` | Responde |
|---|---|
| `jq -r '.level' app.jsonl \| sort \| uniq -c` | Conteo por nivel |
| `jq -c 'select(.level == "error")' app.jsonl` | Solo errores |
| `jq -c 'select(.request_id == "abc")' app.jsonl` | Un request completo |
| `jq -r 'select(.duration_ms > 500) \| [.ts,.event,.duration_ms] \| @tsv' app.jsonl` | Eventos lentos |
| `jq -s 'group_by(.event) \| map({event: .[0].event, n: length})' app.jsonl` | Agregación |
| `head -n 1 app.jsonl \| jq keys` | Esquema del primer evento |

---

## 4. Flujo diario / ejemplo mínimo: logger JSON real

Logger de producción: `dictConfig`, contexto por request, redacción y stdout.

```python
# observabilidad.py
import json, logging, logging.config, random, re, sys, time, uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Callable

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_var: ContextVar[int | None] = ContextVar("user_id", default=None)

SECRETOS = re.compile(r"(?i)(authorization|token|password|secret|api[_-]?key)\s*[:=]\s*\S+")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

def redactar(v: Any) -> Any:
    if isinstance(v, str):
        return EMAIL.sub("[EMAIL_REDACTED]", SECRETOS.sub(r"\1=[REDACTED]", v))
    if isinstance(v, dict):
        return {k: ("[REDACTED]" if re.search(r"(?i)pass|token|secret|authorization", k)
                    else redactar(x)) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [redactar(x) for x in v]
    return v

class ContextoFilter(logging.Filter):
    def filter(self, r: logging.LogRecord) -> bool:
        r.request_id = request_id_var.get() or "-"
        r.user_id = user_id_var.get()
        r.service, r.env, r.version = "pagos-api", "staging", "1.4.2"
        return True

class JsonFormatter(logging.Formatter):
    CAMPOS = ("request_id", "user_id", "service", "env", "version",
              "event_name", "status_code", "duration_ms", "method", "path")
    def format(self, r: logging.LogRecord) -> str:
        d: dict[str, Any] = {
            "ts": datetime.fromtimestamp(r.created, timezone.utc)
                  .isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "level": r.levelname.lower(),
            "logger": r.name,
            "event": r.getMessage(),
        }
        for k in self.CAMPOS:
            v = getattr(r, k, None)
            if v is not None:
                d[k] = redactar(v)
        if r.exc_info:
            d["exception"] = redactar(self.formatException(r.exc_info))
        return json.dumps(d, ensure_ascii=False, separators=(",", ":"), default=str)

CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"contexto": {"()": ContextoFilter}},
    "formatters": {"json": {"()": JsonFormatter}},
    "handlers": {"stdout": {"class": "logging.StreamHandler", "stream": "ext://sys.stdout",
                            "formatter": "json", "filters": ["contexto"], "level": "INFO"}},
    "loggers": {"mi_app": {"handlers": ["stdout"], "level": "INFO", "propagate": False}},
    "root": {"handlers": ["stdout"], "level": "WARNING"},
}
logging.config.dictConfig(CONFIG)
log = logging.getLogger("mi_app.pagos")

class InstrumentacionMiddleware:
    """Instrumentación en middleware mínima, sin dependencias de framework."""
    def __init__(self, siguiente: Callable[[dict], dict]) -> None:
        self.siguiente = siguiente
    def __call__(self, request: dict) -> dict:
        rid = request.get("headers", {}).get("x-request-id") or uuid.uuid4().hex
        token = request_id_var.set(rid)
        user_id_var.set(int(request["user_id"])) if request.get("user_id") else None
        inicio, estado = time.perf_counter(), 500
        try:
            respuesta = self.siguiente(request)
            estado = respuesta.get("status", 200)
            return respuesta
        except Exception:
            log.exception("request.fallo", extra={"event_name": "request"})
            raise
        finally:
            log.info("request.completado", extra={
                "event_name": "http_request", "method": request.get("method"),
                "path": request.get("path"), "status_code": estado,
                "duration_ms": round((time.perf_counter() - inicio) * 1000, 2)})
            request_id_var.reset(token)
            user_id_var.set(None)

def handler(request: dict) -> dict:
    log.info("pago.creado", extra={"event_name": "pago", "monto": request["monto"],
                                   "email": request.get("email")})
    return {"status": 201}

if __name__ == "__main__":
    InstrumentacionMiddleware(handler)({
        "method": "POST", "path": "/pagos", "user_id": 42,
        "headers": {"x-request-id": "req-7f3a"}, "monto": 1999,
        "email": "ana@ejemplo.com", "authorization": "Bearer secreto123"})
```

```bash
python observabilidad.py | tee app.jsonl
# {"ts":"...","level":"info","logger":"mi_app.pagos","event":"pago.creado","request_id":"req-7f3a",
#  "user_id":42,"service":"pagos-api","env":"staging","version":"1.4.2","event_name":"pago",
#  "monto":1999,"email":"[EMAIL_REDACTED]"}
# {"ts":"...","event":"request.completado","request_id":"req-7f3a","status_code":201,
#  "duration_ms":0.31,"method":"POST","path":"/pagos"}
```

Flujo diario:

```bash
python observabilidad.py | jq -c 'select(.level == "info" or .level == "error")'
jq -c . app.jsonl > /dev/null && echo "OK: JSONL válido"
jq -c 'select(.request_id == "req-7f3a")' app.jsonl
jq -r 'select(.duration_ms > 200) | [.ts,.path,.status_code,.duration_ms] | @tsv' app.jsonl
grep -Ei 'Bearer|@[a-z]+\.[a-z]+' app.jsonl || echo "OK: sin secretos/PII"
```

---

## 5. Profundidad: correlación, niveles, agregación y sampling

### Correlation ID

El [[Correlation ID - Request ID]] es el hilo conductor: se genera en el borde (o se respeta el `X-Request-ID` entrante), se guarda en `ContextVar` y se propaga a logs, llamadas HTTP salientes, colas y la respuesta al cliente.

```python
headers = {"X-Request-ID": request_id_var.get() or uuid.uuid4().hex}
```

Usá `uuid4().hex` o el `trace_id` de [[OpenTelemetry]] (si ya hay trazas, **reutilizalo**). Un ID por request; nunca lo uses como etiqueta de métricas (cardinalidad infinita).

### Niveles con criterio

| Nivel | Cuándo | Ejemplo |
|---|---|---|
| `DEBUG` | Detalle de desarrollo, **off** en producción | `cache key=... hit=true` |
| `INFO` | Hecho normal del negocio o ciclo de vida | `pago.creado`, `request.completado` |
| `WARN` | Inesperado pero recuperable | `cache.miss`, retry, fallback |
| `ERROR` | Falló una operación y alguien debe enterarse | `db.conexion_fallida` |
| `CRITICAL` | El proceso no puede continuar | `config.invalida` |

Un `ERROR` por request fallido, no 20. Los `WARN` deben ser accionables. El nivel se decide por **impacto**, no por quién lo lee. Ver [[Niveles de log (DEBUG-INFO-WARN-ERROR)]].

### Negocio vs técnicos, stacktraces y agregación

[[Logs de negocio vs técnicos]] son dos corrientes: `pedido.confirmado` se audita y conserva; `cache.miss` se descarta antes. Sepáralos por `event_name`, `logger` o stream distinto.

`log.exception` dentro de un `except` agrega el traceback; `json.dumps` convierte sus saltos de línea en `\\n` (un evento = una línea). Nunca envíes tracebacks al cliente; ver [[Stacktrace de excepciones]].

```text
app (JSONL por stdout) → [[stdout → CloudWatch - Loki]] → índice → dashboard / alerta
                                                       ├─ p95 de duration_ms por endpoint
                                                       └─ alerta: tasa de error > 2% en 5 min
```

Indexá campos (`level`, `service`, `event`, `status_code`), no el mensaje completo. Alertá sobre **tasas**, no conteos: el tráfico cambia. En [[CloudWatch]] usá *metric filters*; en Loki, LogQL con `| json` y `quantile_over_time`. Con [[OpenTelemetry]], correlacioná `trace_id` del log con la traza.

### Sampling

[[Sampling de logs]] controla volumen y costo:

```python
class SampleFilter(logging.Filter):
    def __init__(self, tasa: float = 0.05) -> None:
        super().__init__()
        self.tasa = tasa
    def filter(self, r: logging.LogRecord) -> bool:
        return r.levelno >= logging.INFO or random.random() < self.tasa
```

- Por nivel: 100% de `WARN+`, 5% de `DEBUG`.
- Por request: muestreá por hash de `request_id` para conservar **todos** los eventos de un request o descartarlos juntos.
- Adaptativo: más muestreo durante incidentes.
- Errores: nunca muestrear salvo bajo ataque (y con alarma).

---

## 6. Configuración avanzada y rendimiento

```python
import queue, logging.handlers
cola: queue.Queue = queue.Queue(maxsize=10_000)
h = logging.StreamHandler(sys.stdout)
h.setFormatter(JsonFormatter())
listener = logging.handlers.QueueListener(cola, h, respect_handler_level=True)
listener.start()
log_async = logging.getLogger("mi_app.async")
log_async.addHandler(logging.handlers.QueueHandler(cola))
log_async.propagate = False
# Al apagar: listener.stop() vacía la cola antes de salir
```

El `ContextoFilter` debe correr **antes** de encolar (en el request) porque el listener corre en otro thread.

| Campo | Cardinalidad | ¿Indexar? |
|---|---|---|
| `level`, `service`, `env`, `status_code` | Baja | ✅ |
| `event_name`, `path` normalizado | Media | ✅ |
| `request_id`, `user_id` | Alta | ⚠️ Solo búsqueda puntual |
| `email`, `ip`, `body`, `token` | Sensible | ❌ Nunca |

Normalizá `/pedidos/123` → `/pedidos/:id`: si no, cada ID crea una serie nueva. Un evento pesa 200-500 bytes: 1.000 req/s ≈ 20-40 GB/día. Usá `ensure_ascii=False` y `separators=(",",":")`; nunca `indent=2`. Rotación local solo si no podés usar stdout (`RotatingFileHandler(maxBytes=50_000_000, backupCount=5)`); en contenedor, `PYTHONUNBUFFERED=1` y sin archivos propios: `docker logs -f <id>` o `kubectl logs -f deploy/api --tail=100`.

---

## 7. Errores comunes: síntoma → causa → solución

| Síntoma | Causa | Solución |
|---|---|---|
| `jq: Cannot parse string` | Mezclaste texto y JSON | Un handler por stdout; sin `print()`; validar con `jq -c .` |
| Líneas partidas en el colector | Traceback multilínea sin escapar | `json.dumps` escapa `\n`; un evento por línea |
| `extra` no aparece | Formatter solo lee campos fijos | Agregá el campo a `CAMPOS` |
| `request_id` siempre `-` | `ContextVar` no se setea en el borde | Generalo en [[Middleware]] y propagalo |
| `request_id` cambia a mitad | Variable global sobrescrita | `ContextVar` + `reset(token)` |
| `AttributeError` con `extra` | Nombre reservado (`message`, `asctime`) | Usá `event_name` |
| Logs duplicados | `propagate=True` + handler en root | `propagate = False` |
| `DEBUG` no aparece | Logger o handler en `INFO` | Ajustá ambos; gana el más alto |
| `logging.exception` sin traceback | Llamada fuera de `except` | Usá `log.error(..., exc_info=True)` |
| Secretos en el panel | Redacción después de `json.dumps` | Redactá en el formatter, antes de serializar |
| Campos `"123"` en vez de `123` | f-strings en `extra` | Pasá tipos reales |
| Miles de series en el dashboard | Alta cardinalidad | Normalizá paths; IDs a campos no indexados |
| Latencia al loggear | I/O síncrono | `QueueHandler` + bajar nivel |
| No hay logs en el contenedor | Sin handler o buffer | `PYTHONUNBUFFERED=1`, configurar logging antes de imports |

---

## 8. Seguridad y buenas prácticas

Ver [[Redacción de PII y secretos]]. Regla de oro: **no loguees lo que no necesitás**. Si necesitás el email, logueá un hash o los últimos 3 caracteres.

```python
# Nunca
log.info(f"login email={email} password={password} token={token}")
log.debug("body: %s", json.dumps(request.body))
# Sí
log.info("login.intentado", extra={"user_id": user.id, "event_name": "auth", "ok": ok})
log.info("request.recibido", extra={"bytes": len(body), "content_type": ctype})
```

- Denylist de claves (`password`, `token`, `secret`, `authorization`, `cookie`) y allowlist de campos en eventos sensibles.
- Redactá **antes** de `json.dumps`; una vez en el string es tarde. Enmascarar en el visor no borra el dato: rotá la credencial expuesta.
- No loguees bodies, headers completos ni cookies; sí `status_code`, `duration_ms`, `bytes`.
- Evitá *log injection*: un `\n` del usuario puede falsificar líneas si concatenás strings; `json.dumps` lo escapa.
- Limitá acceso y retención: los logs son datos personales. Si viajan a terceros, verificá cifrado en tránsito y región.
- `request_id` es identificador, no secreto: podés devolverlo al cliente.

Checklist: JSON válido en todas las líneas · campos obligatorios presentes · `DEBUG` off · redacción en formatter · sin PII · cardinalidad controlada · stdout · sampling por request · `QueueHandler` si el volumen es alto · alertas por tasa.

---

## 9. Ejercicios para dominarlo

1. Ejecutá `observabilidad.py`, canalizá a `app.jsonl` y validá que todas las líneas pasen `jq -c . > /dev/null`.
2. Agregá `pago.rechazado` con `log.exception` y confirmá que `exception` es un string escapado, no multilínea roto.
3. Hacé que el middleware reutilice el `X-Request-ID` entrante y verificá con `jq -c 'select(.request_id == "req-7f3a")'`.
4. Introducí un email y un `Authorization: Bearer ...` y confirmá que se redactan antes de escribir.
5. Configurá `SampleFilter` al 10% para `DEBUG` y 100% para `INFO+`; graficá la distribución con `jq`.
6. Agregá `QueueHandler`/`QueueListener`, enviá 10.000 eventos y compará el tiempo contra logging síncrono.
7. Escribí una consulta de p95 de `duration_ms` por `path` normalizado y una alerta si la tasa de `error` supera 2% en 5 minutos.

---

## 10. Relaciones

[[Logs estructurados]] · [[Formato JSON de logs]] · [[Python logging - Loguru - structlog]] · [[Logger por módulo]] · [[Niveles de log (DEBUG-INFO-WARN-ERROR)]] · [[Correlation ID - Request ID]] · [[Middleware]] · [[Instrumentación en middleware]] · [[Log de request-response + latencia]] · [[Stacktrace de excepciones]] · [[Logs de negocio vs técnicos]] · [[Sampling de logs]] · [[Redacción de PII y secretos]] · [[stdout → CloudWatch - Loki]] · [[CloudWatch]] · [[OpenTelemetry]]
