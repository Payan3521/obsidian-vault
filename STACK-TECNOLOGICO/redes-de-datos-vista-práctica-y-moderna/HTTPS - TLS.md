---
titulo: "HTTPS / TLS"
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
  - "[[CORS]]"
  - "[[CSRF]]"
  - "[[Cadena de confianza]]"
  - "[[Certificados - CA - SNI]]"
  - "[[Cookies]]"
  - "[[Códigos 2xx-3xx-4xx-5xx]]"
  - "[[HSTS]]"
  - "[[HTTP]]"
  - "[[HTTP-2 y HTTP-3]]"
  - "[[Headers - Keep-alive - Compresión gzip-br]]"
---

# HTTPS / TLS — Guía completa 🔐

> ⭐ Núcleo imprescindible. Objetivo: generar certificados, leer un `openssl s_client`, entender el handshake TLS 1.3, configurar nginx y diagnosticar `CERTIFICATE_VERIFY_FAILED` sin copiar ciegamente `-k`.

## 1. Mentalidad: qué es (y qué NO es) HTTPS / TLS

**HTTPS = HTTP sobre TLS.** El protocolo [[HTTP]] no cambia: cambia el transporte. TLS (Transport Layer Security) es una capa entre TCP y la aplicación que aporta tres cosas:

| Propiedad | Cómo la logra |
|---|---|
| **Confidencialidad** | Cifrado simétrico (AES-GCM, ChaCha20-Poly1305) |
| **Integridad** | MAC/AEAD: cualquier modificación del cable invalida el record |
| **Autenticación** | Certificado X.509 firmado por una CA + verificación del nombre |

```text
  HTTP  →  TLS records  →  TCP  →  IP
  GET /  →  [cifrado]   →  puerto 443
```

### Lo que NO es

- ❌ "TLS oculta todo": la IP, el puerto, el SNI (nombre visible en el ClientHello) y el patrón de tráfico suelen verse. Las consultas DNS tampoco se cifran con TLS normal.
- ❌ "Tener certificado = sitio seguro": un certificado solo autentica el nombre. Un sitio con certificado puede tener XSS o SQLi.
- ❌ "HTTPS reemplaza autorización" o a [[CSRF]]: cifra el canal, no valida permisos.
- ❌ "El cifrado es asimétrico todo el rato": la asimétrica solo sirve para acordar la clave; los datos van simétrica (mucho más rápida).
- ❌ "`curl -k` es una solución": desactiva la verificación y anula la autenticación. Úsalo solo en un laboratorio local.
- ❌ "TLS 1.3 y 1.2 son iguales": 1.3 va a 1-RTT, elimina cifrados obsoletos y cifra más del handshake.

### Piezas que debes nombrar bien

| Pieza | Definición rápida |
|---|---|
| **Certificado leaf** | Identifica `ejemplo.com`; contiene clave pública, SAN, emisor y validez |
| **CA intermedia** | Firma el leaf; encadena hasta una root del trust store |
| **Root / trust store** | Ancla de confianza del sistema operativo o navegador |
| **CSR** | Certificate Signing Request: clave pública + datos que envías a la CA |
| **SNI** | Server Name Indication: el nombre en `ClientHello`; permite varios certificados por IP |
| **ALPN** | Negociación de protocolo: `h2`, `http/1.1` (base de [[HTTP-2 y HTTP-3]]) |
| **Cipher suite** | Conjunto de algoritmos de intercambio + cifrado + MAC |
| **Sesión / ticket** | Reanudación para evitar el handshake completo |
| **OCSP / CRL** | Mecanismos para comprobar revocación |

La cadena completa se estudia en [[Cadena de confianza]] y [[Certificados - CA - SNI]]; el protocolo sin cifrar, en [[HTTP]].

> Frase para entrevista: *"TLS autentica el servidor con X.509, negocia una clave efímera con ECDHE y cifra los records con AEAD; HTTP/2 y HTTP/3 se negocian por ALPN"*.

---

## 2. Instalación y primeros pasos

```bash
# Debian / Ubuntu
sudo apt update && sudo apt install -y openssl curl nginx certbot python3-certbot-nginx dnsutils
# Fedora/RHEL: sudo dnf install -y openssl curl nginx certbot python3-certbot-nginx bind-utils
# macOS:      brew install openssl curl nginx certbot

openssl version                 # OpenSSL 3.x
curl -V | grep -i ssl           # TLS compilado en curl
dig +short example.com A
```

### Certificado auto-firmado para laboratorio

```bash
mkdir -p ~/tls-lab && cd ~/tls-lab
openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
  -keyout key.pem -out cert.pem \
  -subj "/C=AR/ST=CABA/L=CABA/O=Lab/OU=Dev/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1, DNS:lab.local"
chmod 600 key.pem

openssl x509 -in cert.pem -noout -subject -issuer -dates
openssl x509 -in cert.pem -noout -ext subjectAltName
```

> El **SAN** manda: desde 2017 `CN` no basta para validar hostname. Si el navegador dice `NET::ERR_CERT_COMMON_NAME_INVALID`, falta el SAN.

### Servidor TLS desnudo con `openssl s_server`

```bash
openssl s_server -accept 8443 -cert cert.pem -key key.pem -www -tls1_3   # terminal 1
```
```bash
openssl s_client -connect localhost:8443 -servername localhost -CAfile cert.pem < /dev/null
curl --cacert ~/tls-lab/cert.pem https://localhost:8443/
curl -k https://localhost:8443/      # ⚠️ solo para comparar el comportamiento
```

### Inspeccionar un sitio real

```bash
echo | openssl s_client -connect example.com:443 -servername example.com -showcerts \
  2>/dev/null | openssl x509 -noout -subject -issuer -dates -ext subjectAltName

curl -vI https://example.com          # ver TLS, ALPN, certificado y headers
curl -sSI https://example.com | grep -iE 'strict-transport|content-security-policy'
```

### nginx con TLS local

```nginx
# /etc/nginx/conf.d/tls-lab.conf
server {
    listen 8443 ssl;
    http2 on;
    server_name localhost;
    ssl_certificate     /home/TU_USUARIO/tls-lab/cert.pem;
    ssl_certificate_key /home/TU_USUARIO/tls-lab/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    location / { return 200 "hola TLS\n"; }
}
```
```bash
sudo nginx -t && sudo systemctl reload nginx
curl --cacert ~/tls-lab/cert.pem https://localhost:8443/
```

### Certificado real con Let's Encrypt

```bash
sudo certbot --nginx -d ejemplo.com -d www.ejemplo.com
sudo certbot certificates
sudo certbot renew --dry-run
systemctl status certbot.timer        # renovación automática
```

---

## 3. Cheat sheet

### Comandos `openssl`

| Comando | Qué hace |
|---|---|
| `openssl req -new -newkey rsa:2048 -nodes -keyout k.pem -out req.csr` | Genera clave + CSR |
| `openssl req -x509 -newkey rsa:2048 -nodes -days 365 -keyout k.pem -out c.pem -addext "subjectAltName=DNS:..."` | Auto-firmado |
| `openssl x509 -in c.pem -noout -text` | Muestra todo el certificado |
| `openssl x509 -in c.pem -noout -dates -issuer -subject -ext subjectAltName` | Datos clave |
| `openssl verify -CAfile ca.pem leaf.pem` | Verifica cadena |
| `openssl s_client -connect host:443 -servername host -showcerts` | Handshake y cadena recibida |
| `openssl s_client -connect host:443 -alpn h2 -tls1_3` | Prueba TLS 1.3 y ALPN |
| `openssl s_server -accept 8443 -cert c.pem -key k.pem -www` | Servidor TLS de prueba |
| `openssl pkcs12 -export -in c.pem -inkey k.pem -out bundle.p12` | Empaquetar para Java/Windows |
| `openssl pkey -in k.pem -noout -text` | Inspeccionar clave (¡cuidado con secretos!) |
| `openssl rand -hex 32` | Generar valor aleatorio |

### `curl` TLS

| Flag | Uso |
|---|---|
| `curl -v https://...` | Muestra versión TLS, cipher, certificado y ALPN |
| `curl -I https://...` | Solo cabeceras (comprobar [[HSTS]]/CSP) |
| `curl --cacert ca.pem https://...` | Confiar en una CA propia |
| `curl --cert client.pem --key client.key https://...` | [[mTLS]] con certificado de cliente |
| `curl --tlsv1.2 --tls-max 1.2` | Forzar TLS 1.2 |
| `curl --tlsv1.3` | Forzar TLS 1.3 |
| `curl --resolve ejemplo.com:443:127.0.0.1 https://ejemplo.com` | Probar un host antes de publicar DNS |
| `curl -k` | ⚠️ Ignora verificación; **nunca en producción** |
| `curl --http2` / `--http3` | Forzar versión de [[HTTP]] sobre TLS |

### Directivas nginx

| Directiva | Para qué |
|---|---|
| `ssl_certificate` / `ssl_certificate_key` | Ruta al certificado y la clave |
| `ssl_protocols TLSv1.2 TLSv1.3;` | Versiones permitidas |
| `ssl_ciphers ...;` / `ssl_conf_command Ciphersuites ...;` | Cifrados (1.2 / 1.3) |
| `ssl_prefer_server_ciphers off;` | Con TLS 1.3 suele dejarse off |
| `ssl_session_cache shared:SSL:10m;` / `ssl_session_timeout 1d;` | Reanudación |
| `ssl_session_tickets off;` o rotación de tickets | Seguridad de reanudación |
| `ssl_stapling on;` + `ssl_stapling_verify on;` | OCSP stapling |
| `ssl_verify_client on;` + `ssl_client_certificate ca.pem;` | [[mTLS]] |
| `http2 on;` / `listen 443 quic reuseport;` | HTTP/2 / HTTP/3 |

### Versiones y cifrados

| Versión | Estado | handshake | Comentario |
|---|---|---|---|
| SSLv2/SSLv3 | ❌ prohibido | — | Vulnerable, desactivar |
| TLS 1.0/1.1 | ❌ deprecado | 2-RTT | Desactivar (BEAST, downgrade) |
| TLS 1.2 | ✅ compatible | 2-RTT | AEAD + ECDHE; mínimo aceptable |
| TLS 1.3 | ✅ recomendado | 1-RTT (0-RTT opcional) | Cifra más del handshake; sin RSA key exchange |

Cifrados modernos: `TLS_AES_128_GCM_SHA256`, `TLS_AES_256_GCM_SHA384`, `TLS_CHACHA20_POLY1305_SHA256` (1.3); `ECDHE-RSA-AES128-GCM-SHA256` / `ECDHE-ECDSA-CHACHA20-POLY1305` (1.2).

---

## 4. Flujo diario / ejemplo mínimo

```bash
cd ~/tls-lab
# 1) Generas material
openssl req -x509 -newkey rsa:2048 -nodes -days 1 -keyout k.pem -out c.pem \
  -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost"

# 2) Levantas servidor y compruebas con curl confiando en tu CA
openssl s_server -accept 8443 -cert c.pem -key k.pem -www -tls1_3 &   # terminal 1
curl --cacert c.pem https://localhost:8443/                           # terminal 2

# 3) Inspeccionas el handshake
echo | openssl s_client -connect localhost:8443 -servername localhost \
  -CAfile c.pem -alpn h2 -showcerts 2>/dev/null \
  | grep -E 'Protocol|Cipher|Verify return code|ALPN|subject='

# 4) Verificas headers de seguridad
curl -sSI https://localhost:8443/ | grep -iE 'strict-transport|content-security-policy'

# 5) Antes de publicar DNS, pruebas el vhost
curl --resolve ejemplo.com:443:127.0.0.1 --cacert c.pem https://ejemplo.com/

# 6) Limpieza
kill %1
```

Salida sana de `s_client`: `Protocol : TLSv1.3`, `Verify return code: 0 (ok)`, `ALPN protocol: h2`.

---

## 5. Profundidad: handshake, cadena y reanudación

### TLS 1.3 (1-RTT)

```text
Cliente ── ClientHello: SNI, versiones, key_share (ECDHE), ALPN, cifrados ──▶ Servidor
Cliente ◀── ServerHello + Certificate + CertificateVerify + Finished ─────── Servidor
Cliente ── Finished ──▶  ✓ claves de aplicación listas
Cliente ◀══════ HTTP/2 o HTTP/1.1 dentro de records cifrados ══════▶
```

- El **key_share** contiene la clave pública efímera del cliente (X25519). El servidor responde con la suya: ambos derivan la misma clave sin enviarla.
- `CertificateVerify` es una firma con la clave privada del servidor: prueba que posee el certificado.
- `Finished` confirma que todo el handshake fue íntegro.
- TLS 1.3 cifra el certificado y los extensiones: antes el observador veía más información.

### TLS 1.2 (2-RTT, resumen)

```text
ClientHello → ServerHello → Certificate → ServerKeyExchange → ServerHelloDone
ClientKeyExchange → ChangeCipherSpec → Finished → ChangeCipherSpec → Finished → datos
```

Con RSA key exchange estático no hay *forward secrecy*: si robas la clave privada hoy, puedes descifrar tráfico grabado ayer. Con ECDHE cada sesión usa una clave efímera → sí hay forward secrecy.

### Reanudación y 0-RTT

| Mecanismo | Cómo funciona | Riesgo |
|---|---|---|
| Session ID (1.2) | Servidor guarda estado por ID | Memoria en servidor |
| Session ticket (1.2/1.3) | Estado cifrado en el cliente | Rotar clave de tickets |
| PSK (1.3) | Reutiliza secreto derivado | Perfect forward secrecy solo parcial |
| 0-RTT (1.3) | Datos en el primer vuelo | ⚠️ **Replay**: no enviar pagos ni mutaciones |

### Cadena de confianza

```text
leaf (ejemplo.com)  ← firmada por  intermediate (R3)  ← firmada por  root (ISRG Root X1)
        ↑ verifying: openssl verify -CAfile ca.pem -untrusted intermediate.pem leaf.pem
```

- El servidor debe enviar **leaf + intermedios** (`fullchain.pem`), nunca solo el leaf.
- El cliente construye la cadena hasta una root de su trust store; si falta un intermedio sale `unable to get local issuer certificate`.
- SNI ([[Certificados - CA - SNI]]) permite varios certificados en la misma IP; un `servername` distinto al SAN provoca hostname mismatch.
- Revocación: OCSP stapling evita que el cliente consulte al CA (mejor privacidad y latencia).

### Emisión con ACME

1. El cliente ACME (`certbot`) crea una cuenta con clave.
2. Prueba control del dominio con **HTTP-01** (archivo en `/.well-known/acme-challenge/`) o **TLS-ALPN-01**.
3. Envía CSR → la CA emite leaf + intermedio.
4. `certbot` despliega y configura renovación; renovar a los ~60 días de 90.

### Relación con el resto de la pila

- [[HTTP-2 y HTTP-3]]: `h2` se negocia por ALPN sobre TLS 1.2+; HTTP/3 incorpora TLS 1.3 dentro de QUIC.
- [[Headers - Keep-alive - Compresión gzip-br]]: la reanudación TLS y el keep-alive se complementan: uno abarata el handshake, el otro evita repetirlo.
- [[Códigos 2xx-3xx-4xx-5xx]]: `301 http→https`, `200` tras el handshake, `421` por SNI/vhost mal mapeado.
- [[Cookies]] con `Secure` + [[SameSite]] viajan solo sobre TLS; [[Sesiones]] y [[JWT]] dependen de ese canal.
- [[HSTS]] obliga al navegador a usar TLS; [[CORS]] requiere `https://` en origins; [[OAuth 2.0]] y [[OpenID Connect]] exigen HTTPS en redirects; [[SAML]] firma aserciones sobre TLS; [[WebSockets]] usa `wss://`, [[SSE]] `https://`, [[gRPC]] `https://` con ALPN `h2`.

---

## 6. Configuración avanzada y rendimiento

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name ejemplo.com www.ejemplo.com;

    ssl_certificate     /etc/letsencrypt/live/ejemplo.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ejemplo.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_session_cache   shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;                       # o rotar la clave de tickets
    ssl_stapling on;  ssl_stapling_verify on;
    resolver 1.1.1.1 8.8.8.8 valid=300s;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;

    return 301 https://ejemplo.com$request_uri;    # solo en el vhost canónico
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
openssl s_client -connect ejemplo.com:443 -servername ejemplo.com -status < /dev/null 2>/dev/null | grep -A2 'OCSP Response'
curl -sSI https://ejemplo.com | grep -i strict-transport
```

### Optimizaciones

- **Certificado ECDSA P-256**: más chico y rápido que RSA-2048; sirve un segundo certificado RSA para clientes antiguos (`ssl_certificate` dos veces).
- **AES-NI**: CPU moderna hace AES-GCM muy barato; en móviles, ChaCha20-Poly1305 suele ganar.
- **Session resumption**: baja el handshake de 2-RTT a 1-RTT (0-RTT con PSK).
- **Terminación en el edge/CDN**: el TLS se negocia cerca del usuario; internamente puedes usar [[mTLS]] o red privada.
- **OCSP stapling + HSTS preload**: menos latencia y menos ventanas de downgrade.
- **keep-alive y HTTP/2**: no pagues un handshake por request ([[Headers - Keep-alive - Compresión gzip-br]]).
- **Renovación automatizada**: `certbot.timer` o ACME en CI; monitoriza días restantes.

```bash
# Benchmark burdo del handshake
openssl s_time -connect ejemplo.com:443 -servername ejemplo.com -new -www / -time 5
openssl speed ecdsap256 rsa2048 aes-128-gcm      # rendimiento criptográfico local
```

> ⚠️ Con TLS 1.3 **no** configures cifrados con `ssl_ciphers`: usa `ssl_conf_command Ciphersuites TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256;`.

---

## 7. Errores comunes (síntoma → causa → solución)

| Síntoma | Causa | Solución |
|---|---|---|
| `curl: (60) SSL certificate problem: self signed certificate` | CA no confiable | `curl --cacert ca.pem`; instala la CA interna |
| `unable to get local issuer certificate` | Falta intermedio en `fullchain.pem` | Usar `fullchain.pem`; `openssl verify -CAfile ca.pem -untrusted int.pem leaf.pem` |
| `NET::ERR_CERT_COMMON_NAME_INVALID` | El nombre no está en el SAN | Regenerar con `-addext "subjectAltName=DNS:..."` |
| `NET::ERR_CERT_DATE_INVALID` / `certificate has expired` | Certificado vencido o reloj mal sincronizado | Renovar; `timedatectl status`; `openssl x509 -noout -dates` |
| `Verify return code: 20 (unable to get local issuer certificate)` | Cadena incompleta | Ver siguiente enlace de la cadena |
| `ssl_error_no_cypher_overlap` / `no shared cipher` | Sin cifrado común | Habilitar TLS 1.2 AEAD; revisar `ssl_ciphers` |
| `unsupported protocol` / `Protocol version TLSv1.0 disabled` | Cliente o servidor con TLS antiguo | Arrancar con `-tls1_2`/`-tls1_3`; desactivar versiones viejas |
| `ALPN, server did not agree to a protocol` | `http2 on` ausente o cliente sin ALPN | `curl --http2`; revisar `openssl s_client -alpn h2` |
| `535 Incorrect authentication data` en SMTP / `400` en mTLS | Certificado de cliente ausente o CA incorrecta | `--cert/--key`; `ssl_client_certificate ca.pem` |
| `502` del proxy hacia upstream HTTPS | Proxy no confía en el certificado interno | Añadir CA al trust store del proxy o `proxy_ssl_verify off` (solo controlado) |
| `certbot: Challenge failed (http-01)` | Puerto 80 bloqueado o redirecciónmal puesta | Permitir `/.well-known/acme-challenge/` sin redirección; revisar DNS |
| `too many certificates already issued` | Rate limit de la CA | Usar `--dry-run` y staging de Let's Encrypt |
| Sitio en bucle `http → https → http` | Redirección duplicada (proxy + app) | Redirigir solo en una capa; revisar `X-Forwarded-Proto` |
| `SSL: CERTIFICATE_VERIFY_FAILED` en Python | Falta CA en el trust store de Python | Instalar `certifi`; no uses `verify=False` |
| Mixed content bloqueado en el navegador | Recursos `http://` dentro de página HTTPS | Cambiar todos los assets a `https://` o rutas relativas |
| HSTS impide cargar después de expirar | `max-age` alto grabado en el navegador | Renovar **antes** de vencer; `chrome://net-internals` para limpiar en dev |

### Diagnóstico ordenado

```bash
dig +short ejemplo.com A                                  # 1) DNS
echo | openssl s_client -connect ejemplo.com:443 -servername ejemplo.com \
  -showcerts 2>/dev/null | openssl x509 -noout -dates -ext subjectAltName   # 2) cadena
curl -vI https://ejemplo.com                              # 3) TLS + headers
sudo nginx -t && sudo tail -n 100 /var/log/nginx/error.log # 4) servidor
```

---

## 8. Seguridad y buenas prácticas

1. **TLS 1.2 mínimo, TLS 1.3 preferido**; prohibir SSLv3/TLS 1.0/1.1 y cifrados RC4/3DES/CBC estáticos.
2. **Forward secrecy**: solo ECDHE/DHE; nunca RSA key exchange.
3. **HSTS** ([[HSTS]]): `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`. Solicita preload solo cuando estés seguro: no hay vuelta atrás rápida.
4. **CSP** (texto plano): `Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'`. TLS cierra el canal; CSP frena XSS.
5. **Certificados**: SAN correcto, cadena completa, renovación automática, claves `chmod 600`, nunca compartir la privada ni commitearla. Monitoriza Certificate Transparency.
6. **CAA** en DNS: `ejemplo.com. CAA 0 issue "letsencrypt.org"` limita quién puede emitir.
7. **Cookies**: `Secure`, `HttpOnly`, [[SameSite]]; [[CSRF]] y [[CORS]] no se arreglan con TLS ([[Cookies]]).
8. **Autenticación**: [[JWT]] con `exp` corto, [[OAuth 2.0]] + PKCE, [[OpenID Connect]] para identidad; HTTPS obligatorio en `redirect_uri`.
9. **OWASP Top 10** (texto plano): inyección, access control roto, XSS, SSRF. TLS es una capa, no un sustituto.
10. **mTLS** ([[mTLS]]) para comunicación servicio a servicio: verifica también al cliente.
11. **No confíes en `X-Forwarded-*`** desde Internet: configura `set_real_ip_from` y `real_ip_header` en el proxy.
12. **Logs sin secretos**: nunca logues claves privadas, tokens ni cookies de sesión ([[Sesiones]]).
13. **Actualiza** OpenSSL/nginx y revisa la config con `nginx -t` y un escáner de TLS en cada release.

---

## 9. Ejercicios para dominarlo

1. Genera un auto-firmado con SAN `DNS:localhost,IP:127.0.0.1` y comprueba que `curl` falla sin `--cacert` y funciona con él.
2. Levanta `openssl s_server` en TLS 1.3 y lee `Protocol`, `Cipher`, `Verify return code` y `ALPN` desde `s_client`.
3. Crea una CA propia, firma un CSR con `openssl x509 -req -CA ca.pem -CAkey ca.key -CAcreateserial` y verifica la cadena con `-CAfile`.
4. Quita el intermedio de `fullchain.pem`, recarga nginx y reproduce `unable to get local issuer certificate`; restaura la cadena.
5. Fuerza `curl --tlsv1.2` contra un servidor solo 1.3 y explica el error; prueba al revés.
6. Configura OCSP stapling y HSTS en nginx; verifica ambos con `openssl s_client -status` y `curl -I`.
7. Simula un preflight con origen `https://` y una cookie `Secure; SameSite=None`: explica qué exige [[CORS]] y por qué `Secure` es obligatorio.

---

## 10. Relaciones

[[HTTP]] · [[HTTPS - TLS]] · [[HTTP-2 y HTTP-3]] · [[Headers - Keep-alive - Compresión gzip-br]] · [[Códigos 2xx-3xx-4xx-5xx]] · [[Métodos HTTP (GET-POST-PUT-PATCH-DELETE)]] · [[Certificados - CA - SNI]] · [[Cadena de confianza]] · [[mTLS]] · [[HSTS]] · [[CORS]] · [[Cookies]] · [[SameSite]] · [[CSRF]] · [[Sesiones]] · [[JWT]] · [[OAuth 2.0]] · [[OpenID Connect]] · [[SAML]] · [[WebSockets]] · [[SSE]] · [[gRPC]]
