---
titulo: "Middleware"
categoria:
  - "15. Arquitectura y diseño"
tags:
  - "mapa-tecnologico"
  - "nivel-dominar"
  - "arquitectura-y-diseño"
  - "guia-completa"
nivel: dominar
estrella: true
tipo: guia
estado: completa
actualizado: 2026-11-24
relacionado_con:
  - "[[CORS]]"
  - "[[Logs estructurados]]"
  - "[[Manejo de errores]]"
  - "[[JWT]]"
  - "[[Active Record vs Data Mapper]]"
  - "[[Controller]]"
  - "[[DAO]]"
  - "[[DTO]]"
  - "[[Dependency Injection]]"
  - "[[Interceptor - Filter]]"
  - "[[Mapper]]"
  - "[[Model - Entity]]"
  - "[[Repository]]"
  - "[[Service]]"
---

# Middleware — Guía completa 🧩

> ⭐ Núcleo imprescindible. Objetivo: saber qué va en la cadena de request, en qué **orden**, cómo cortocircuitar, y diferenciarlo de [[Interceptor - Filter]], [[Controller]] y [[Service]].

## 1. Mentalidad: qué es (y qué NO es)

Un middleware es una **pieza pequeña y composable** que se coloca en el camino de una petición para hacer algo *cross-cutting* antes o después del handler: loguear, autenticar, validar, medir, manejar errores,限 limitar tasa, comprimir, abrir una transacción.

```text
Request ──▶ CORS ──▶ Logger ──▶ Auth ──▶ Validación ──▶ [[Controller]]
                                                          │
                                                     [[Service]] → [[Repository]] → DB
Response ◀── CORS ◀── Logger ◀── Auth ◀── Validación ◀──────┘
```

 Es el patrón **cadena de responsabilidad**: cada eslabón decide `next()` o responde sin pasar. Se dice *modelo cebolla*: el primer middleware envuelve a los demás y ve el antes **y** el después.

### Qué NO es

- ❌ **No es lógica de negocio**: eso va en [[Service]]; el middleware no calcula precios ni aplica reglas del dominio.
- ❌ **No es el handler**: el [[Controller]] decide qué respuesta dar; el middleware solo condiciona el camino.
- ❌ **No es un message broker**: también existe "middleware de mensajería" (colas, publish/subscribe), pero aquí hablamos del pipeline HTTP.
- ❌ **No es lo mismo que un [[Interceptor - Filter]]**: el filtro suele trabajar a nivel de contenedor/servlet y el interceptor es AOP; el middleware es una cadena explícita del framework.
- ❌ **No es gratis**: cada eslabón añade llamadas, asignaciones y, si es síncrono, bloqueo.

| Concepto | Capa | Ejemplo |
|---|---|---|
| Middleware | Pipeline HTTP | `app.use(cors())`, `@app.middleware("http")` |
| [[Interceptor - Filter]] | Contenedor / AOP | `HandlerInterceptor`, `@Around` |
| [[Controller]] | Adaptación HTTP | `@GetMapping`, `router.get()` |
| [[Service]] | Casos de uso | `crearUsuario()`, `calcularTotal()` |
| [[Repository]] / [[DAO]] | Persistencia | `findById()`, SQL |
| [[Model - Entity]] / [[DTO]] | Datos | Entidad JPA / payload de entrada |

> Frase para entrevista: *"Middleware es comportamiento transversal en la cadena de request; el orden importa porque cada eslabón puede cortocircuitar o envolver a los siguientes"*.

---

## 2. Instalación y primeros pasos

### Express (Node)

```bash
node -v && npm -v
mkdir -p ~/mw-lab && cd ~/mw-lab && npm init -y
npm i express cors helmet express-rate-limit morgan jsonwebtoken
node app.js
```

```js
// app.js
const express = require('express');
const app = express();

app.use((req, res, next) => {                 // middleware artesanal
  req.id = crypto.randomUUID();
  console.log(req.id, req.method, req.originalUrl);
  res.setHeader('X-Request-ID', req.id);
  next();                                    // ⚠️ sin esto el request se cuelga
});

app.use(express.json({ limit: '1mb' }));
app.get('/health', (req, res) => res.json({ ok: true }));
app.listen(3000, () => console.log('listen :3000'));
```

```bash
curl -sS -i http://localhost:3000/health       # 200 + X-Request-ID
curl -sS -X POST http://localhost:3000/health -H 'Content-Type: application/json' -d '{}'
```

### FastAPI / Starlette (Python)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn python-multipart
uvicorn main:app --reload --port 8000
```

```python
# main.py
from fastapi import FastAPI, Request
from time import perf_counter
from uuid import uuid4

app = FastAPI()

@app.middleware("http")
async def observabilidad(request: Request, call_next):
    rid = str(uuid4())
    request.state.request_id = rid
    t0 = perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    response.headers["X-Response-Time"] = f"{perf_counter() - t0:.4f}s"
    return response

@app.get("/health")
async def health():
    return {"ok": True}
```

```bash
curl -sS -i http://localhost:8000/health | grep -iE 'HTTP/|x-request-id|x-response-time'
```

### Django y Spring (Referencia rápida)

```python
# settings.py — Django
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]
```

```java
// Spring Boot
@Component
public class RequestIdFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest req,
                                    HttpServletResponse res, FilterChain chain)
            throws ServletException, IOException {
        res.setHeader("X-Request-ID", UUID.randomUUID().toString());
        chain.doFilter(req, res);              // equivalente a next()
    }
}
```

```bash
# Go (net/http): middleware es func(http.Handler) http.Handler
# Laravel: php artisan make:middleware VerifyToken
# Registro: $middleware, $middlewareGroups, $routeMiddleware
```

---

## 3. Cheat sheet

### Tipos de middleware

| Tipo | Qué hace | Dónde va | Riesgo |
|---|---|---|---|
| Logging / trazas | Request ID, method, duración, status | **Primero** | Loguear secretos/PII |
| CORS | Cabeceras `Access-Control-*` y preflight | Antes de auth (OPTIONS) | `*` con credenciales |
| Seguridad (helmet) | CSP, `X-Content-Type-Options`, HSTS | Muy temprano | Romper assets externos |
| Autenticación | Valida [[JWT]] / sesión; llena `req.user` | Antes del [[Controller]] | Aceptar `alg: none` |
| Autorización | Comprueba roles/scope | Después de autenticar | Confundir 401 con 403 |
| Validación | Parsea y valida [[DTO]] de entrada | Antes del handler | Body leído dos veces |
| Body parser | `application/json`, `multipart` | Antes de rutas | Límites y DoS |
| Rate limit | Cuota por IP/usuario/token | Temprano | `X-Forwarded-For` falso |
| Manejo de errores | Convierte excepciones en respuesta | **Al final** de la cadena | Swallow bugs sin log |
| Caché / compresión | `Cache-Control`, gzip/br | Cerca de la salida | `Vary` olvidado |
| Transacción / Unit of Work | Abierta al entrar, commit/rollback al salir | Envolviendo [[Service]] | Transacciones largas |
| Métricas / health | Contadores, latencia, `/health` | Primero o junto a logs | Coste por request |

### Registro por framework

| Framework | Sintaxis |
|---|---|
| Express | `app.use(fn)`; `app.use(path, fn)`; `app.use(err, req, res, next)` |
| FastAPI | `@app.middleware("http")` / `add_middleware(...)` |
| Django | Lista `MIDDLEWARE` en `settings.py` |
| Spring Boot | `Filter` / `OncePerRequestFilter`, `HandlerInterceptor`, `@ControllerAdvice` |
| Gin (Go) | `r.Use(mw1, mw2)`; `c.Next()`; `c.Abort()` |
| Laravel | `Kernel::$middleware`, `->middleware('auth')` en rutas |

### Códigos que suele devolver el middleware

| Código | Significado típico en la cadena |
|---|---|
| `401` | Falta o expiró el token (autenticación) |
| `403` | Token válido sin permiso (autorización) |
| `413` | Body mayor al límite del parser |
| `415` | `Content-Type` no soportado |
| `422` | [[DTO]] inválido |
| `429` | Rate limit; cabecera `Retry-After` |
| `500` | Excepción no manejada → [[Manejo de errores]] |
| `200` | Preflight `OPTIONS` respondido por CORS |

---

## 4. Flujo diario / ejemplo mínimo

```bash
# 1) Cadena completa en Express: logger → CORS → body → JWT → rutas → errores
cat > app.js <<'EOF'
const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const app = express();

app.use((req, res, next) => {
  console.log(JSON.stringify({ reqId: crypto.randomUUID(), method: req.method, path: req.path }));
  next();
});
app.use(cors({ origin: 'https://app.ejemplo.com', credentials: true }));
app.use(express.json({ limit: '256kb' }));

function auth(req, res, next) {
  const token = (req.headers.authorization || '').replace(/^Bearer\s+/i, '');
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET, { algorithms: ['HS256'] });
    next();
  } catch {
    res.status(401).json({ error: 'unauthorized' });   // cortocircuito
  }
}

app.get('/health', (_, res) => res.json({ ok: true }));   // público, sin auth
app.get('/me', auth, (req, res) => res.json({ user: req.user.sub }));

app.use((err, req, res, next) => {                        // middleware de error (4 args)
  console.error(err);
  res.status(err.status || 500).json({ error: 'internal', reqId: req.id });
});
app.listen(3000);
EOF
JWT_SECRET='cambia-este-secreto' node app.js
```

```bash
# 2) Verificas cada eslabón
curl -sS http://localhost:3000/health                                  # 200, sin token
curl -sS -i http://localhost:3000/me                                   # 401
TOKEN=$(node -e "console.log(require('jsonwebtoken').sign({sub:'ana'},'cambia-este-secreto'))")
curl -sS -H "Authorization: Bearer $TOKEN" http://localhost:3000/me     # {"user":"ana"}

# 3) Preflight: lo responde CORS, no el controller
curl -sS -i -X OPTIONS http://localhost:3000/me \
  -H 'Origin: https://app.ejemplo.com' -H 'Access-Control-Request-Method: GET'
```

Flujo mental: **¿el middleware corre?** (log) → **¿llega al handler?** (`next()`) → **¿qué status sale?** (`401`/`403`/`429`) → **¿el error pasa al manejador final?**.

---

## 5. Profundidad: orden, cortocircuito y estado

### Modelo cebolla

```text
entrada:  A → B → C → handler
salida:   A ← B ← C ← handler
```

Si `A` registra `t0` antes de `next()`, puede calcular la duración **después** de `next()`. Por eso el logger va primero y el manejador de errores, al final.

### Reglas de orden

1. **Request ID, logging y métricas**: primero, para cubrir también los fallos.
2. **Seguridad de cabeceras y CORS**: antes de auth; el preflight `OPTIONS` debe responderse sin exigir token.
3. **Body parser / validación**: antes de rutas que lean `req.body`.
4. **Autenticación** → **autorización**: no puedes autorizar a quien no identificaste.
5. **Rate limit**: temprano para no gastar CPU en requests que vas a rechazar.
6. **Rutas / [[Controller]]**.
7. **Manejo de errores**: último, con firma de 4 parámetros en Express.

> En FastAPI/Starlette los `@app.middleware("http")` se apilan en **orden inverso** al de declaración: el último declarado es el más externo. Verifícalo siempre con logs.

### Cortocircuito

- `return res.status(401)...` detiene la cadena: los middleware posteriores **no corren**.
- En Express: `next()` continúa, `next(err)` salta al manejador de error, `res.send()` corta.
- En Gin: `c.Next()` / `c.Abort()`.
- En Spring: `chain.doFilter(...)` / devolver sin llamarlo.

### Estado por request y [[Dependency Injection]]

- `req.user`, `request.state.request_id` o `HttpContext.Items` son **request-scoped**.
- Nunca guardes estado de usuario en una variable global del módulo: se mezcla entre concurrentes.
- Prefiere [[Dependency Injection]] para inyectar el repositorio o servicio en el [[Controller]]; el middleware solo **enriquece el contexto**.
- La validación produce un [[DTO]]; el [[Mapper]] lo convierte a [[Model - Entity]]; [[Repository]] o [[DAO]] persisten. Con [[Active Record vs Data Mapper]] cambia dónde vive la persistencia, no el lugar del middleware.
- Si el middleware abre una transacción, el patrón [[Unit of Work]] decide el commit al salir de la cadena.

### [[Logs estructurados]] y correlación

```json
{"ts":"2026-11-24T12:00:00Z","reqId":"b3f1…","method":"GET","path":"/me","status":401,"ms":3.2}
```

- Un `X-Request-ID` generado al entrar y propagado a [[Service]]/[[ Repository]] permite seguir un request completo.
- Añade `status` y duración **en la salida**, no al entrar.
- Nunca logues `Authorization`, `Cookie`, passwords ni tokens.

### [[Manejo de errores]] centralizado

- Un solo middleware de error convierte excepciones en JSON consistente: `{ "error": "code", "reqId": "..." }`.
- Diferencia errores de cliente (4xx, esperados) de errores de servidor (5xx, con stack solo en logs).
- En producción no devuelvas stack traces; devuelve un ID correlacionable.

### [[JWT]] en el pipeline

```text
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
                       └─ header ─┘└──── payload ────┘└─ firma ─┘
```

```bash
TOKEN='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbmEifQ.signature'
echo "$TOKEN" | cut -d. -f2 | base64 -d 2>/dev/null    # decodificar payload (demo)
```

Valida siempre **firma, `alg`, `exp`, `nbf`, `iss` y `aud`**. Un middleware que solo decodifica el payload sin verificar la firma es una puerta abierta.

### [[CORS]] y preflight

- `Origin` distinto + método no simple → el navegador envía `OPTIONS` primero.
- El middleware de [[CORS]] debe responder ese `OPTIONS` con `Access-Control-Allow-Origin`, `-Methods`, `-Headers` y `-Max-Age`, **antes** de exigir autenticación.
- Con credenciales, `Allow-Origin` no puede ser `*` y hay que responder `Vary: Origin` para no envenenar la caché.

---

## 6. Configuración avanzada y rendimiento

| Práctica | Por qué |
|---|---|
| `app.use(path, fn)` o rutas con `middleware` selectivo | No pagues JWT en `/health` ni en assets |
| Rutas de exclusión en logger/auth | Menos ruido y menos coste |
| Body parser con `limit` y `verify` | Evita DoS por payload gigante |
| Rate limit en memoria para dev, store compartido para producción | Varias réplicas necesitan contador centralizado |
| Middleware async donde haya I/O | No bloquees el event loop / thread pool |
| Comprimir respuestas grandes, con `Vary: Accept-Encoding` | Menos bytes; caché correcta |
| Caché de `GET` idempotentes antes del [[Controller]] | Responde sin tocar [[Repository]] |
| `X-Request-ID` propagado al upstream | Trazas extremo a extremo |
| Timeouts y `AbortController` | Un middleware colgado no retiene recursos |
| Graceful shutdown | Cierra pools y deja terminar requests en vuelo |

```js
// Solo aplicar autenticación donde hace falta
app.use('/api', authMiddleware);          // Express
app.get('/health', healthHandler);        // queda fuera
```

```python
# FastAPI: excluir rutas del middleware
@app.middleware("http")
async def solo_api(request: Request, call_next):
    if request.url.path.startswith("/health"):
        return await call_next(request)
    # ... lógica costosa ...
    return await call_next(request)
```

```bash
# Verificación de cabeceras y latencia introducida por la cadena
curl -sS -D - -o /dev/null http://localhost:3000/me -H "Authorization: Bearer $TOKEN" \
  | grep -iE 'HTTP/|x-request-id|x-response-time|access-control'
wrk -t2 -c50 -d10s http://localhost:3000/health   # comparar antes/después de añadir middleware
```

> Regla: **midiendo, no opinando**. Un middleware de logging síncrono con writes por request puede dominar la latencia; usa cola/buffer o logging asíncrono.

---

## 7. Errores comunes (síntoma → causa → solución)

| Síntoma | Causa | Solución |
|---|---|---|
| El request se cuelga sin respuesta | Falta `next()` / `chain.doFilter()` | Llamarlo o responder explícitamente |
| `Cannot set headers after they are sent` | Doble respuesta: middleware y handler | Cortocircuita con `return` tras `res.send()` |
| `401` en el preflight `OPTIONS` | Auth corre antes que [[CORS]] | Mover CORS antes o excluir `OPTIONS` |
| `No 'Access-Control-Allow-Origin' header` | Falta middleware de [[CORS]] o `Vary: Origin` | Configurar origins explícitos |
| `Authorization` llega vacío al handler | Parser o auth consume el header | No mutar `req.headers`; guarda en `req.user` |
| `Unexpected token` al leer `req.body` | Body leído dos veces o `Content-Type` incorrecto | Un solo parser; `-H 'Content-Type: application/json'` |
| `413 Request Entity Too Large` | Límite del body parser | Ajustar `limit`, rechazar con JSON claro |
| Error `500` sin body útil | Falta middleware de error al final | Registrar manejador con 4 argumentos / `@ControllerAdvice` |
| Excepción "swallowed" (no aparece) | `catch` sin `next(err)` ni log | Relanzar o pasar al manejador central |
| `req.user` es de otro usuario | Estado global en vez de request-scoped | Usar `req.*` / `request.state` / DI |
| Rate limitbloquea a todos detrás de un NAT | Se usa IP del proxy | Configurar trusted proxies y `X-Forwarded-For` |
| Latencia sube mucho al añadir logs | Log síncrono por request | Logging asíncrono / muestreo / buffer |
| Transacción no hace rollback | El error no pasa por el middleware que la abrió | `next(err)` y commit/rollback en `finally` |
| CORS funciona en `curl` pero no en el navegador | `curl` no aplica CORS | Probar desde el navegador o con preflight `OPTIONS` |
| Cabeceras de seguridad duplicadas | Helmet + nginx añaden lo mismo | Elegir una capa; revisar con `curl -I` |

### Depuración rápida

```bash
curl -v -i http://localhost:3000/me -H "Authorization: Bearer $TOKEN"
node --inspect app.js            # o logs con reqId y timestamps
tail -f /var/log/app/structured.log | jq 'select(.status >= 400)'
```

---

## 8. Seguridad y buenas prácticas

1. **CORS estricto** ([[CORS]]): lista blanca de origins; `credentials: true` solo con origin explícito y `Vary: Origin`.
2. **JWT** ([[JWT]]): verificar firma con algoritmo fijo, `exp`, `iss`, `aud`; rechazar `alg: none`; no guardar el access token en `localStorage` sin Need.
3. **Cookies** con `HttpOnly`, `Secure`, `SameSite`; CSRF (texto plano) requiere token o doble submit en mutaciones.
4. **Cabeceras de seguridad**: CSP, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, HSTS; aplícalas en una sola capa.
5. **Body limits** y validación de [[DTO]]: rechaza lo que no esperas, con `415`/`422`.
6. **Rate limiting** y backoff: protege login y endpoints costosos; cuenta por usuario, no solo por IP.
7. **OWASP Top 10** (texto plano): inyección, broken access control, SSRF y logging excesivo. El middleware es tu primera línea, no la única.
8. **Fail closed**: si falla la validación del token, deniega; nunca continúes "por si acaso".
9. **Logs sanitizados** ([[Logs estructurados]]): sin secretos, con `reqId`, method, status y duración.
10. **Errores consistentes** ([[Manejo de errores]]): mismo formato JSON en toda la cadena; stack traces solo en logs.
11. **Confía en `X-Forwarded-*` solo desde proxies conocidos**: configura trusted proxies antes de limitar por IP.
12. **[[Dependency Injection]]** para servicios y repositorios; evita `new` dentro del middleware.
13. **Revisa el orden** en cada release: un cambio de posición puede desactivar autenticación sin que los tests lo noten.

---

## 9. Ejercicios para dominarlo

1. Escribe un middleware artesanal en Express que añada `X-Request-ID` y mida duración; comprueba ambas cabeceras con `curl -i`.
2. Invierte el orden de `cors()` y `auth` y observa cómo cambia el preflight `OPTIONS`; corrígelo.
3. Implementa un middleware de [[JWT]] que valide `exp` y `aud`; prueba un token vencido y confirma `401`.
4. Crea un manejador de errores central y lanza una excepción desde un [[Service]]: verifica que el cliente recibe JSON y el log conserva el stack.
5. Añade rate limit con límite 2 y haz 4 peticiones: confirma `429` y `Retry-After`.
6. Mide latencia con `wrk` antes y después de añadir logging síncrono; explica la diferencia y cambia a asíncrono.
7. Dibuja la cadena incluyendo [[Controller]], [[Service]], [[Repository]], [[Mapper]] y [[DTO]], y marca dónde entran [[Unit of Work]] y [[Interceptor - Filter]].

---

## 10. Relaciones

[[Middleware]] · [[Controller]] · [[Service]] · [[Repository]] · [[DAO]] · [[Model - Entity]] · [[DTO]] · [[Mapper]] · [[Active Record vs Data Mapper]] · [[Unit of Work]] · [[Dependency Injection]] · [[Interceptor - Filter]] · [[CORS]] · [[JWT]] · [[Logs estructurados]] · [[Manejo de errores]]
