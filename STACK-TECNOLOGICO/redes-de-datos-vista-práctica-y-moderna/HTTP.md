---
titulo: "HTTP"
categoria:
  - "11. Redes de datos (vista práctica y moderna)"
tags:
  - "mapa-tecnologico"
  - "nivel-dominar"
  - "redes-de-datos-vista-práctica-y-moderna"
  - "guia-completa"
nivel: dominar
estrella: true
tipo: guia
estado: completa
actualizado: 2026-11-24
relacionado_con:
  - "[[HTTPS - TLS]]"
  - "[[CORS]]"
  - "[[CSRF]]"
  - "[[Cadena de confianza]]"
  - "[[Certificados - CA - SNI]]"
  - "[[Cookies]]"
  - "[[Códigos 2xx-3xx-4xx-5xx]]"
  - "[[HSTS]]"
  - "[[HTTP-2 y HTTP-3]]"
  - "[[Headers - Keep-alive - Compresión gzip-br]]"
---

# HTTP — Guía completa 🌐

> ⭐ Núcleo imprescindible. Objetivo: manejar `curl` sin pensarlo, leer un intercambio crudo, entender caché / keep-alive / HTTP/2 y /3, y saber por qué una response es `401`, `403` o `429`.

## 1. Mentalidad: qué es (y qué NO es) HTTP

HTTP es un **protocolo de aplicación request/response**. Cliente envía un mensaje, servidor devuelve otro. Define **sintaxis de mensajes**, métodos, códigos y headers; no define cómo se almacena nada ni "sesiones mágicas".

```text
  Cliente                                    Servidor
     |── GET /v1/usuarios?limit=10 HTTP/1.1 ──▶|
     |   Host: api.ejemplo.com                  |
     |   Accept: application/json               |
     |◀── HTTP/1.1 200 OK ──────────────────────|
     |   Content-Type: application/json         |
     |   ETag: "a1b2c3"                         |
     |   [{"id":1,"nombre":"Ana"}]              |
```

### Ideas que hay que fijar

| Idea | Definición rápida |
|---|---|
| **Stateless** | Cada request se procesa de forma independiente; el servidor no "recuerda" la anterior salvo que tú lo implementes con [[Cookies]], [[Sesiones]] o [[JWT]]. |
| **Recurso vs representación** | La URI identifica un recurso; la response contiene una **representación** (JSON, HTML, XML). |
| **Método** | Intención del cliente: leer, crear, reemplazar, modificar, borrar. Ver [[Métodos HTTP (GET-POST-PUT-PATCH-DELETE)]]. |
| **Código de estado** | Resultado del intento: [[Códigos 2xx-3xx-4xx-5xx]]. |
| **Header** | Metadatos del mensaje. Controlan caché, negociación, autenticación, CORS, etc. |
| **Seguro / idempotente** | *Safe* = no modifica estado (`GET`, `HEAD`). *Idempotente* = repetirlo deja el mismo estado (`GET`, `PUT`, `DELETE`). |
| **Conexión** | TCP (HTTP/1.1, HTTP/2) o QUIC/UDP (HTTP/3). No es lo mismo que "sesión de aplicación". |

### Mitos que conviene desterrar

- ❌ "HTTP es HTTPS pero sin contraseña" → **HTTPS es HTTP sobre TLS** (ver [[HTTPS - TLS]]).
- ❌ "HTTP/2 cambia los métodos y los códigos" → no; cambia el **framing** y la multiplexación ([[HTTP-2 y HTTP-3]]).
- ❌ "Un `200` significa que la operación de negocio salió bien" → significa que el servidor procesó el request; el payload puede traer `{"error": true}`.
- ❌ "HTTP es orientado a conexión" → HTTP/1.1 **reutiliza** TCP con keep-alive; HTTP/3 ni usa TCP.
- ❌ "El body solo va en POST" → `PUT`, `PATCH`, `DELETE` y hasta `GET` pueden tenerlo (aunque los intermediarios lo tratan raro).
- ❌ "CORS es seguridad del servidor" → CORS protege al **navegador**; `curl` no lo aplica ([[CORS]]).

> Frase para entrevista: *"HTTP es un protocolo stateless de aplicación; el estado y la seguridad los construye la aplicación encima, con TLS, cookies/tokens y control de acceso"*.

---

## 2. Instalación y primeros pasos

### Herramientas del oficio

```bash
# Debian / Ubuntu
sudo apt update && sudo apt install -y curl wget netcat-openbsd dnsutils nginx openssl jq

# Fedora / RHEL
sudo dnf install -y curl wget nmap-ncat bind-utils nginx openssl jq

# Arch
sudo pacman -S curl wget netcat dnsutils nginx openssl jq

# macOS
brew install curl wget httpie openssl nginx jq

# Verificación
curl --version | head -2
curl -V | grep -i ssl
dig +short example.com A
```

### Servidor local en 30 segundos

```bash
mkdir -p /tmp/http-lab && cd /tmp/http-lab
echo '{"ok":true,"mensaje":"hola HTTP"}' > datos.json

# Terminal 1: servidor estático
python3 -m http.server 8080 --bind 127.0.0.1
```

```bash
# Terminal 2: clientes
curl -v http://127.0.0.1:8080/datos.json      # intercambio completo por stderr
curl -i http://127.0.0.1:8080/datos.json      # cabeceras + body
curl -sS -D - -o /dev/null http://127.0.0.1:8080/datos.json   # solo headers
curl -sS http://127.0.0.1:8080/datos.json | jq .             # JSON bonito
curl -I http://127.0.0.1:8080/datos.json                     # request HEAD
```

### Ver el protocolo crudo con `nc`

```bash
# Terminal 1: escucha
nc -l 127.0.0.1 9999

# Terminal 2: request escrito a mano (¡\r\n importa!)
printf 'GET /hola HTTP/1.1\r\nHost: localhost:9999\r\nAccept: */*\r\n\r\n' \
  | nc 127.0.0.1 9999
```

Verás exactamente `GET /hola HTTP/1.1`, `Host:` y la respuesta del servidor. Es el mejor ejercicio para interiorizar que HTTP es **texto estructurado** (en HTTP/1.1).

### nginx mínimo

```bash
sudo systemctl enable --now nginx
curl -sSI http://localhost
sudo tail -f /var/log/nginx/access.log
```

```nginx
# /etc/nginx/conf.d/lab.conf
server {
    listen 8081;
    server_name localhost;

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Request-ID $request_id;
    }
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
curl -sS -i http://localhost:8081/api/health
```

### DNS y HTTPIE (opcional pero útil)

```bash
dig +short example.com A
dig example.com CNAME +short
python3 -m pip install --user httpie
http GET https://httpbin.org/get X-Debug:1
http POST https://httpbin.org/post nombre=Ana  # JSON automático
```

---

## 3. Cheat sheet

### Métodos

| Método | Intención | Safe | Idempotente | Típico código |
|---|---|:---:|:---:|---|
| `GET` | Leer recurso | ✅ | ✅ | `200` / `304` |
| `HEAD` | Igual que GET, sin body | ✅ | ✅ | `200` |
| `POST` | Crear / acción no idempotente | ❌ | ❌ | `201` / `200` / `303` |
| `PUT` | Reemplazar recurso completo | ❌ | ✅ | `200` / `204` |
| `PATCH` | Modificación parcial | ❌ | ⚠️ (depende) | `200` / `204` |
| `DELETE` | Borrar recurso | ❌ | ✅ | `204` / `200` |
| `OPTIONS` | Descubrir métodos soportados | ✅ | ✅ | `204` + `Allow` |
| `TRACE` | Eco del request (desactivar) | ✅ | ✅ | `200` / `405` |
| `CONNECT` | Túnel, base de HTTPS proxies | — | — | `200` |

### Códigos de estado

| Código | Nombre | Cuándo usarlo |
|---|---|---|
| `100` | Continue | Cliente envía `Expect: 100-continue` |
| `200` | OK | Éxito genérico |
| `201` | Created | Creado; poner `Location: /recursos/42` |
| `202` | Accepted | Aceptado para procesamiento asíncrono |
| `204` | No Content | Éxito sin body (típico `DELETE`) |
| `301` | Moved Permanently | Redirección permanente; cacheable |
| `302` | Found | Redirección temporal |
| `304` | Not Modified | Caché sigue vigente (sin body) |
| `307` / `308` | Temporary / Permanent Redirect | Redirección **sin cambiar** método ni body |
| `400` | Bad Request | Sintaxis / validación inválida |
| `401` | Unauthorized | Falta credencial (**autenticación**) |
| `403` | Forbidden | Autenticado pero sin permiso (**autorización**) |
| `404` | Not Found | No existe (o no quieres revelar que existe) |
| `405` | Method Not Allowed | Enviar header `Allow` |
| `409` | Conflict | Conflicto de estado (ej. versión, duplicado) |
| `415` | Unsupported Media Type | `Content-Type` no aceptado |
| `422` | Unprocessable Content | Sintaxis OK, semántica inválida |
| `429` | Too Many Requests Rate limiting; enviar `Retry-After` |
| `500` | Internal Server Error | Bug del servidor |
| `502` | Bad Gateway | Proxy recibió respuesta inválida del upstream |
| `503` | Service Unavailable | Caído / sobrecarga; `Retry-After` |
| `504` | Gateway Timeout | Upstream tardó demasiado |

### Headers imprescindibles

| Header | Lado | Para qué sirve |
|---|---|---|
| `Host` | request | Obligatorio en HTTP/1.1; permite virtual hosts y SNI |
| `Accept` | request | Negociación de representación (`application/json`) |
| `Content-Type` | ambos | Tipo del body (`application/json; charset=utf-8`) |
| `Content-Length` / `Transfer-Encoding: chunked` | ambos | Delimitación del body |
| `Authorization: Bearer …` | request | Token ([[JWT]], [[OAuth 2.0]]) |
| `Cookie` / `Set-Cookie` | ambos | [[Cookies]], [[Sesiones]], [[SameSite]] |
| `Cache-Control` | ambos | `max-age`, `no-store`, `private`, `immutable` |
| `ETag` / `If-None-Match` | ambos | Caché condicional → `304` |
| `Last-Modified` / `If-Modified-Since` | ambos | Caché condicional por fecha |
| `Vary` | response | Clave de caché dependiente de headers (`Accept-Encoding`, `Origin`) |
| `Location` | response | Redirecciones y `201` |
| `Connection: keep-alive` | ambos | Reutilización TCP ([[Headers - Keep-alive - Compresión gzip-br]]) |
| `Accept-Encoding` / `Content-Encoding` | ambos | `gzip`, `br` |
| `Origin` / `Access-Control-Allow-Origin` | request/response | [[CORS]] |
| `Referer` / `Referrer-Policy` | request/response | Privacidad de navegación |
| `Strict-Transport-Security` | response | [[HSTS]] |
| `Content-Security-Policy` | response | Política de scripts/recursos (CSP) |
| `X-Request-ID` / `Traceparent` | ambos | Correlación de logs |

### `curl` que usarás a diario

| Comando | Qué hace |
|---|---|
| `curl -i URL` | Incluye headers de respuesta |
| `curl -I URL` | Solo headers (HEAD) |
| `curl -v URL` | Verboso: DNS, TCP, TLS, request y response |
| `curl -sS URL` | Silencioso pero muestra errores |
| `curl -X POST -H 'Content-Type: application/json' -d '{"a":1}' URL` | POST JSON |
| `curl --compressed URL` | Envía `Accept-Encoding` y descomprime |
| `curl -L URL` | Sigue redirecciones |
| `curl -o archivo URL` / `curl -O URL` | Guardar body |
| `curl -w '%{http_code} %{time_total}\n' -o /dev/null URL` | Métricas |
| `curl --connect-timeout 5 --max-time 20 --retry 3 URL` | Timeouts y reintentos |
| `curl -H 'Authorization: Bearer TOKEN' URL` | Autenticación |
| `curl --cacert ca.pem URL` | Confiar en CA propia |
| `curl -k URL` | ⚠️ Desactiva verificación TLS (solo debug local) |
| `curl --http1.1` / `--http2` / `--http3` | Fuerza versión |
| `curl -A 'MiAgente/1.0' -e 'https://origen'` | User-Agent y Referer |

---

## 4. Flujo diario / ejemplo mínimo

```bash
# 1) Arrancas tu API en local
uvicorn main:app --reload --port 8000

# 2) Healthcheck rápido
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/health   # 200

# 3) Creas un recurso
curl -sS -i -X POST http://127.0.0.1:8000/usuarios \
  -H 'Content-Type: application/json' \
  -d '{"nombre":"Ana","email":"ana@ejemplo.com"}'
# HTTP/1.1 201 Created
# Location: /usuarios/1

# 4) Lo lees con condicional
ETAG=$(curl -sSI http://127.0.0.1:8000/usuarios/1 \
  | awk 'tolower($1)=="etag:"{gsub(/\r/,"",$2); print $2}')
echo "$ETAG"    # "W/\"9f8a\""

curl -sS -o /dev/null -w '%{http_code}\n' \
  -H "If-None-Match: $ETAG" http://127.0.0.1:8000/usuarios/1   # 304

# 5) Validación y errores
curl -sS -i -X POST http://127.0.0.1:8000/usuarios \
  -H 'Content-Type: application/json' -d '{"email":"no-es-email"}'
# 422 Unprocessable Content

# 6) Medición
curl -sS -o /dev/null -w 'dns=%{time_namelookup} tcp=%{time_connect} ttfb=%{time_starttransfer} total=%{time_total} size=%{size_download}\n' \
  http://127.0.0.1:8000/usuarios
```

Flujo mental del día a día: **¿llega el request?** (`-v`) → **¿qué código devuelve?** (`-i`) → **¿qué headers manda?** (`-I`) → **¿es caché, CORS o autenticación?** (sección 7).

---

## 5. Profundidad: lo que ocurre entre `-v` y el JSON

### Anatomía cruda de un intercambio

```text
GET /v1/usuarios?limit=2 HTTP/1.1\r\n
Host: api.ejemplo.com\r\n
User-Agent: curl/8.5\r\n
Accept: */*\r\n
Accept-Encoding: gzip, deflate, br\r\n
Connection: keep-alive\r\n
\r\n
```

```text
HTTP/1.1 200 OK\r\n
Date: Tue, 24 Nov 2026 12:00:00 GMT\r\n
Content-Type: application/json; charset=utf-8\r\n
Content-Length: 58\r\n
Cache-Control: private, max-age=60\r\n
ETag: "9f8a"\r\n
Vary: Accept-Encoding\r\n
\r\n
[{"id":1,"nombre":"Ana"},{"id":2,"nombre":"Bea"}]
```

### Del TCP a HTTP/2 y HTTP/3

```text
HTTP/1.1: [TCP 3-way handshake] ── req1 ── resp1 ── req2 ── resp2 ── (misma conexión)
HTTP/2:   [TCP + TLS ALPN "h2"] ── stream1 ─┬─ stream3 ─┬─ stream5 ─▶ (multiplex)
HTTP/3:   [QUIC/UDP 1-RTT] ───── frames sobre stream independientes ─────▶
```

| Versión | Transporte | Problema que resuelve | Detalle |
|---|---|---|---|
| HTTP/1.0 | TCP | — | Una conexión por request |
| HTTP/1.1 | TCP | Reutilización | keep-alive, chunked; pipelining sufre *head-of-line blocking* |
| HTTP/2 | TCP + TLS | Concurrencia | Multiplexing binario, HPACK, priorización, server push |
| HTTP/3 | QUIC sobre UDP | HOL blocking de TCP | 0-RTT/1-RTT, QPACK, migración de conexión |

Detalles en [[HTTP-2 y HTTP-3]] y [[Headers - Keep-alive - Compresión gzip-br]].

### Keep-alive y pools

- `Connection: keep-alive` + `Keep-Alive: timeout=5, max=100` en HTTP/1.1.
- El **pool de conexiones** del cliente evita repetir DNS + TCP + TLS en cada llamada.
- Un `Content-Length` incorrecto o un chunked mal cerrado rompe la reutilización: el cliente cree que el body terminó antes.
- En nginx: `keepalive_timeout 30s; keepalive_requests 1000;`.

### Caché (el origen de la mitad de los bugs "no veo el cambio")

```bash
# Petición condicional completa
URL='https://httpbin.org/etag/mi-version'
curl -sS -D /tmp/h1 -o /tmp/b1 "$URL"
ETAG=$(awk 'tolower($1)=="etag:"{gsub(/\r/,"",$2); print $2}' /tmp/h1)
curl -sS -D - -o /dev/null -H "If-None-Match: $ETAG" "$URL" | head -5
# HTTP/2 304 Not Modified  → el body viaja vacío
```

| Directiva | Significado |
|---|---|
| `max-age=60` | Frescura por 60 s |
| `s-maxage=600` | Solo para cachés compartidas (CDN/proxy) |
| `no-cache` | Puede guardar, pero **debe revalidar** |
| `no-store` | No guardar en ningún sitio (datos sensibles) |
| `private` | Solo caché del navegador |
| `public` | También proxy/CDN |
| `immutable` | No revalidar durante `max-age` (assets con hash) |
| `stale-while-revalidate=30` | Servir stale mientras se revalida |

- `Vary: Accept-Encoding` evita servir gzip a un cliente que no lo entiende.
- `Vary: Origin` es imprescindible cuando la respuesta depende de [[CORS]].
- **Truco**: añade `?v=20261124` a un asset para forzar invalidación.

### Compresión

```bash
curl -sS --compressed -H 'Accept-Encoding: br, gzip' \
  -o /dev/null -w 'transfer=%{size_download} bytes\n' https://example.com
```

`Content-Encoding` indica cómo viene el body; `Content-Type` sigue siendo el tipo lógico. Comprimir JSON ahorra muchísimo; no tiene sentido comprimir imágenes JPEG/PNG ya comprimidas.

### CORS en la práctica

```bash
# Preflight real de un navegador
curl -sS -i -X OPTIONS https://api.ejemplo.com/usuarios \
  -H 'Origin: https://app.ejemplo.com' \
  -H 'Access-Control-Request-Method: PUT' \
  -H 'Access-Control-Request-Headers: authorization,content-type'
```

La respuesta debe incluir `Access-Control-Allow-Origin: https://app.ejemplo.com`, `Allow-Methods`, `Allow-Headers` y, si hay cookies, `Access-Control-Allow-Credentials: true` **con un origin explícito** (nunca `*`). Más en [[CORS]].

### Estado: cookies, sesiones y tokens

```text
Set-Cookie: sid=abc123; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600   → [[Sesiones]]
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...                                  → [[JWT]]
```

- [[Cookies]] con `HttpOnly` no son legibles por JavaScript (mitiga XSS).
- [[SameSite]=Lax|Strict]([[SameSite]]) limita el envío en peticiones cross-site; [[CSRF]] requiere además token/validación de origin.
- [[OAuth 2.0]] maneja **autorización**; [[OpenID Connect]] añade identidad; [[SAML]] es el estándar enterprise basado en XML.
- [[WebSockets]] arranca con un `Upgrade` HTTP; [[SSE]] es un stream HTTP largo; [[gRPC]] usa HTTP/2.

### Idempotencia y reintentos

Un cliente puede reintentar `PUT`/`GET` con seguridad; reintentar `POST` puede duplicar cobros. Por eso se usan claves de idempotencia (`Idempotency-Key: …`) y códigos `409` para conflictos.

---

## 6. Configuración avanzada y rendimiento

### nginx bien afinado

```nginx
http {
    sendfile            on;
    tcp_nopush          on;
    keepalive_timeout   30s;
    keepalive_requests  1000;
    client_max_body_size 10m;

    gzip on;
    gzip_vary on;
    gzip_comp_level 5;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript application/xml;

    server {
        listen 443 ssl;
        http2 on;                       # HTTP/2 sobre TLS (ver [[HTTPS - TLS]])
        server_name ejemplo.com;

        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;  # [[HSTS]]

        location /assets/ {
            add_header Cache-Control "public, max-age=31536000, immutable" always;
            try_files $uri =404;
        }

        location /api/ {
            proxy_pass http://127.0.0.1:8000;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_read_timeout 30s;
            proxy_connect_timeout 5s;
        }
    }
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
curl -sSI https://ejemplo.com/assets/app.js | grep -iE 'cache-control|content-encoding|strict-transport'
```

### HTTP/3 en nginx (cuando tu build lo soporta)

```nginx
server {
    listen 443 ssl;
    listen 443 quic reuseport;
    http3 on;
    add_header Alt-Svc 'h3=":443"; ma=86400' always;
}
```

### Checklist de rendimiento

- [ ] Reutiliza conexiones: keep-alive en cliente **y** proxy.
- [ ] Habilita HTTP/2 o HTTP/3 ([[HTTP-2 y HTTP-3]]).
- [ ] `gzip`/`br` para texto; `Vary: Accept-Encoding`.
- [ ] Caché de assets con hash + `immutable`; HTML con `no-cache`.
- [ ] Miniifica y usa sprites/CDN; reduce round-trips con `preconnect`.
- [ ] Carga útil pequeña: paginación, `fields=`, evitar `SELECT *`.
- [ ] `Retry-After` y backoff exponencial en `429`/`503`.
- [ ] Timeouts en **todos** los clientes (`--connect-timeout`, `--max-time`).
- [ ] Observa TTFB, no solo `time_total`.
- [ ] Mide con `curl -w` y logs con `$request_time`.

```bash
curl -sS -o /dev/null -w \
'dns=%{time_namelookup} connect=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer} total=%{time_total} bytes=%{size_download}\n' \
  https://example.com
```

---

## 7. Errores comunes (síntoma → causa → solución)

| Síntoma | Causa | Solución |
|---|---|---|
| `curl: (6) Could not resolve host` | DNS no resuelve | `dig +short dominio A`; revisar `/etc/resolv.conf` o el nombre |
| `curl: (7) Failed to connect … Connection refused` | Servidor caído o puerto cerrado | `ss -ltnp | grep :8000`; arrancar el servicio |
| `curl: (28) Operation timed out` | Firewall, ruta o servidor lento | `--connect-timeout`, `--max-time`; revisar `iptables`/SG |
| `HTTP/1.1 301` en bucle | Redirección mal configurada | `curl -I` paso a paso; revisar `Location` y `server_name` |
| `301` cambia POST por GET | 301/302 históricos | Usar `307`/`308` para conservar método y body |
| `401` inesperado | Falta o expiró el token | `Authorization: Bearer …`; revisar `exp` del [[JWT]] |
| `403` con token válido | Falta autorización/scope/origin | Revisar roles, `aud` del token y regex de [[CORS]] |
| `415 Unsupported Media Type` | `Content-Type` ausente o distinto | `-H 'Content-Type: application/json'` |
| `422` aunque el JSON es válido | Validación de negocio | Leer el body del error; no es un problema de sintaxis |
| `413 Request Entity Too Large` | `client_max_body_size` / límite del framework | Subir el límite o hacer upload por partes |
| `429 Too Many Requests` | Rate limiting | Esperar `Retry-After`, backoff y jitter |
| `500` solo en producción | Config/secret/distinto entorno | Comparar variables; ver logs del servidor |
| `502 Bad Gateway` | Upstream caído o respuesta inválida | `curl` directo al upstream; revisar `proxy_pass` |
| `504 Gateway Timeout` | Upstream lento | Subir `proxy_read_timeout` **y** arreglar la lentitud |
| `304` con body vacío | Comportamiento correcto | No es error: revalida caché con `If-None-Match` |
| `CORS policy: No 'Access-Control-Allow-Origin'` | Falta header o `Vary: Origin` | Configurar origins explícitos ([[CORS]]) |
| `curl: (52) Empty reply from server` | Servidor cerró sin response | `nginx -t`, logs, `curl -v` |
| Basura binaria en la terminal | Response comprimida sin descomprimir | Añadir `--compressed` |
| `405 Method Not Allowed` | Método no soportado | Revisar header `Allow`; usar `OPTIONS` |

### Forense rápido

```bash
curl -v --trace-ascii /tmp/trace.txt https://ejemplo.com 2>/dev/null
sed -n '1,40p' /tmp/trace.txt
sudo tail -n 100 /var/log/nginx/error.log
ss -tanp | grep ESTAB | head
```

---

## 8. Seguridad y buenas prácticas

1. **Todo sobre TLS**: usa [[HTTPS - TLS]] siempre; redirige `80 → 443` y añade [[HSTS]]:
   ```text
   Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
   ```
2. **CSP** (cabecera, no enlace):
   ```text
   Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'
   ```
3. **Cookies**: `HttpOnly`, `Secure`, [[SameSite]]=Lax/Strict, `Path`, expiración corta ([[Cookies]]).
4. **CSRF**: tokens sincronizados o doble submit en mutaciones con cookies ([[CSRF]]).
5. **CORS**: lista blanca de origins; `*` solo para APIs públicas sin credenciales ([[CORS]]).
6. **JWT**: valida `alg`, `exp`, `iss`, `aud`; no aceptes `alg: none`; guarda el refresh token en cookie `HttpOnly` ([[JWT]]).
7. **Identidad**: [[OAuth 2.0]] con PKCE para clientes públicos; [[OpenID Connect]] para login; [[SAML]] en enterprise.
8. **OWASP Top 10** (texto plano): inyección, broken access control, XSS, SSRF, deserialización insegura. Validar entrada y escapar salida.
9. **No reveles stack traces** en `500`; devuelve un ID de error y correlaciona con logs ([[Códigos 2xx-3xx-4xx-5xx]]).
10. **Desactiva `TRACE`**, oculta `Server`/`X-Powered-By`, limita body y rate-limit.
11. **Certificados**: cadena completa y SNI correcto ([[Cadena de confianza]], [[Certificados - CA - SNI]]); en entornos estrictos, [[mTLS]].
12. **Logs sin secretos**: nunca logues `Authorization`, `Cookie` ni passwords.
13. **Actualiza**: versiones de nginx/framework y cipher suites; revisa cabeceras con `curl -I` en cada release.

---

## 9. Ejercicios para dominarlo

1. Levanta `python3 -m http.server 8080` y captura con `nc` un `GET`; escribe el request a mano con `\r\n` y explica cada línea.
2. Con `curl -v` sobre `https://example.com`, identifica DNS, TCP, TLS, ALPN y el primer byte del body.
3. Pide `https://httpbin.org/etag/abc` dos veces con `If-None-Match` y confirma el `304`; explica por qué no hay body.
4. Simula un preflight CORS con `OPTIONS` y comprueba la diferencia entre `*` y un origin explícito ([[CORS]]).
5. Provoca `401`, `403`, `404`, `415`, `429` y `502` en tu API local; documenta la causa real de cada uno.
6. Configura nginx con gzip + `Vary: Accept-Encoding` + `Cache-Control immutable` y verifica las cabeceras con `curl -I`.
7. Mide `dns`, `connect`, `ttfb` y `total` con `curl -w` antes y después de activar keep-alive/HTTP/2; explica la diferencia.

---

## 10. Relaciones

[[HTTP-2 y HTTP-3]] · [[HTTPS - TLS]] · [[CORS]] · [[CSRF]] · [[Cadena de confianza]] · [[Certificados - CA - SNI]] · [[Cookies]] · [[SameSite]] · [[Sesiones]] · [[JWT]] · [[OAuth 2.0]] · [[OpenID Connect]] · [[SAML]] · [[Códigos 2xx-3xx-4xx-5xx]] · [[Headers - Keep-alive - Compresión gzip-br]] · [[Métodos HTTP (GET-POST-PUT-PATCH-DELETE)]] · [[HSTS]] · [[mTLS]] · [[WebSockets]] · [[SSE]] · [[gRPC]]
