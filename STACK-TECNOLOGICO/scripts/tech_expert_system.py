# -*- coding: utf-8 -*-
"""
Motor experto de generación de fichas técnicas para tecnologías y conceptos de ingeniería de software.
Si la nota tiene ya una guía completa en Obsidian, se extrae y formatea.
Para el resto de tecnologías, el motor provee explicaciones rigurosas y específicas basadas
en su categoría, nombre y patrones reconocidos.
"""

import re, html

# Diccionario de conceptos de alto impacto con definiciones técnicas minuciosas
DEEP_CONCEPTS = {
    "cors": {
        "title": "CORS (Cross-Origin Resource Sharing)",
        "category": "Redes de datos & Seguridad Web",
        "what": "Mecanismo de seguridad implementado de forma obligatoria por los navegadores web que utiliza cabeceras HTTP específicas para permitir o denegar que una aplicación web cargada en un origen (protocolo, dominio y puerto) acceda a recursos ubicados en un origen diferente.",
        "why": "Por diseño, la web aplica la política del mismo origen (Same-Origin Policy o SOP) para evitar que sitios maliciosos roben sesiones o datos bancarios desde la pestaña abierta de un usuario. CORS resuelve la necesidad legítima de conectar frontends (ej. React en localhost:3000 o vercel.app) con APIs alojadas en dominios distintos (ej. api.empresa.com) sin desproteger al usuario final.",
        "how": "1. Peticiones simples: Si el método es GET/POST con cabeceras estándar, el navegador envía la cabecera 'Origin'. El servidor debe responder con 'Access-Control-Allow-Origin: <origen>'. Si no coincide, el navegador bloquea la lectura del cuerpo de la respuesta.\n2. Peticiones con pre-vuelo (Preflight): Para métodos como PUT, DELETE, PATCH o cabeceras personalizadas ('Authorization', 'Content-Type: application/json'), el navegador envía automáticamente una petición HTTP OPTIONS previa. El servidor responde con 'Access-Control-Allow-Methods', 'Access-Control-Allow-Headers' y 'Access-Control-Max-Age'. Solo si el preflight es aprobado, el navegador despacha la petición real.",
        "good_practices": "• NUNCA usar 'Access-Control-Allow-Origin: *' en producción cuando se manejan credenciales o cookies ('Access-Control-Allow-Credentials: true'); los navegadores rechazarán la petición por protocolo.\n• Configurar CORS a nivel de API Gateway o Reverse Proxy (Nginx, Traefik, Kong) para evitar código duplicado en cada microservicio.\n• Comprender que CORS NO protege al servidor de atacantes con scripts (curl, Postman, Python) ya que estos no implementan SOP; CORS protege a los navegadores de tus clientes.",
        "example": "HTTP/1.1 204 No Content\nAccess-Control-Allow-Origin: https://app.dominio.com\nAccess-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\nAccess-Control-Allow-Headers: Content-Type, Authorization\nAccess-Control-Allow-Credentials: true\nAccess-Control-Max-Age: 86400"
    },
    "docker": {
        "title": "Docker & Contenedores OCI",
        "category": "Contenerización e Infraestructura",
        "what": "Plataforma de virtualización a nivel de sistema operativo que empaqueta una aplicación y todo su árbol de dependencias (runtimes, librerías del sistema, binarios y configuraciones) en una unidad inmutable y portátil llamada contenedor.",
        "why": "Erradica por completo el problema clásico de 'en mi máquina sí funcionaba'. Provee entornos consistentes y reproducibles desde la laptop del desarrollador local hasta los clústeres de producción en la nube, optimizando el uso de recursos frente a las máquinas virtuales pesadas.",
        "how": "No virtualiza hardware completo ni corre un kernel secundario. Aprovecha características nativas del kernel de Linux: 1) Namespaces (aísla PID, redes, montajes de disco, IPC y usuarios), 2) Cgroups (limita y audita consumo de memoria RAM, cuotas de CPU e I/O), y 3) Union Filesystem / Overlay2 (capas de lectura apiladas con una capa superior delgada de lectura/escritura copy-on-write).",
        "good_practices": "• Usar imágenes base mínimas (Distroless o Alpine) para reducir superficie de ataque y peso en red.\n• Implementar multi-stage builds en el Dockerfile para compilar binarios en una etapa y empaquetar únicamente el artefacto final en la imagen de producción.\n• Nunca ejecutar el proceso principal dentro del contenedor como usuario 'root'. Usar la directiva USER.",
        "example": "# Multi-stage build optimizado\nFROM golang:1.22-alpine AS builder\nWORKDIR /app\nCOPY . .\nRUN CGO_ENABLED=0 go build -o server .\n\nFROM gcr.io/distroless/static-debian12\nCOPY --from=builder /app/server /server\nUSER nonroot:nonroot\nENTRYPOINT [\"/server\"]"
    },
    "git": {
        "title": "Git — Sistema de Control de Versiones Distribuido",
        "category": "Control de Versiones y Flujo de Código",
        "what": "Sistema de control de versiones descentralizado y de alto rendimiento que rastrea los cambios realizados en archivos a lo largo del tiempo, garantizando la integridad criptográfica de todo el historial de un proyecto de software.",
        "why": "Permite el trabajo colaborativo simultáneo entre cientos de ingenieros sobre una misma base de código, habilitando ramificación barata (branches), reversión instantánea de bugs y auditoría completa de quién, cuándo y por qué se modificó cada línea.",
        "how": "Opera como una base de datos de objetos direccionables por su contenido (content-addressable storage) en la carpeta '.git/objects'. Cada archivo se almacena como un 'blob' identificado por su hash criptográfico SHA-1/SHA-256; los directorios se guardan como 'trees' y los commits son objetos que apuntan a un tree raíz y a sus commits padres. Las ramas son simplemente punteros atómicos ligeros (archivos de 41 bytes) que avanzan con cada commit.",
        "good_practices": "• Mantener commits pequeños y atómicos que hagan una sola cosa bien, siguiendo la especificación Conventional Commits (feat, fix, refactor, chore).\n• Nunca modificar ni reescribir ramas públicas compartidas (evitar git push --force sin validación; preferir --force-with-lease).\n• Familiarizarse con 'git reflog' para rescatar commits o ramas aparentemente eliminadas por error.",
        "example": "# Flujo de trabajo atómico\ngit checkout -b feat/user-auth-jwt\ngit add -p\ngit commit -m \"feat(auth): implement JWT token verification middleware\"\ngit push origin feat/user-auth-jwt"
    },
    "postgresql": {
        "title": "PostgreSQL — SGBD Relacional Objeto-Relacional Avanzado",
        "category": "Bases de Datos & Persistencia",
        "what": "Sistema de gestión de bases de datos relacional y de código abierto de nivel empresarial, con soporte completo para transacciones ACID, tipado avanzado, JSON nativo y extensibilidad de motor.",
        "why": "Es la base de datos de referencia para cargas de trabajo críticas que exigen cero tolerancia a la pérdida o corrupción de datos. Ofrece consistencia estricta, consultas analíticas complejas y extensiones clave como PostGIS (geoespacial) y pgvector (vectores para IA).",
        "how": "Utiliza una arquitectura multiproceso con memoria compartida (shared buffers). La durabilidad y consistencia se garantizan mediante el registro previo de escritura WAL (Write-Ahead Logging): antes de modificar una página de datos en disco, el cambio se escribe secuencialmente en el WAL. El aislamiento se logra con MVCC (Multi-Version Concurrency Control), donde las lecturas nunca bloquean escrituras y viceversa porque cada transacción ve una foto fija inmutable (snapshot) de los datos.",
        "good_practices": "• Monitorizar el proceso de VACUUM para evitar el 'bloat' de tablas y wraparound de IDs de transacción en tablas de alta tasa de escrituras/actualizaciones.\n• Diseñar índices con propósito: B-Tree para comparaciones de rango e igualdad; GIN para columnas JSONB, arrays o búsquedas vectoriales.\n• Utilizar siempre un connection pooler (ej. PgBouncer) en producción para amortiguar el coste de abrir miles de procesos de conexión concurrentes.",
        "example": "-- Creación de tabla con JSONB e índice GIN optimizado\nCREATE TABLE transacciones (\n    id BIGSERIAL PRIMARY KEY,\n    usuario_id UUID NOT NULL,\n    detalles JSONB NOT NULL,\n    creado_en TIMESTAMPTZ DEFAULT NOW()\n);\nCREATE INDEX idx_transacciones_detalles ON transacciones USING gin(detalles);"
    },
    "sql": {
        "title": "SQL (Structured Query Language) & Motor Relacional",
        "category": "Bases de Datos",
        "what": "Lenguaje declarativo estandarizado (ANSI/ISO) para definir esquemas de datos (DDL), manipular registros (DML), controlar accesos (DCL) y orquestar transacciones (TCL) en sistemas de bases de datos relacionales.",
        "why": "Permite desacoplar el 'QUÉ' datos se necesitan del 'CÓMO' se deben buscar en disco. El optimizador de consultas del motor se encarga de elegir la ruta de ejecución más rápida mediante estadísticas de costos.",
        "how": "El motor parsea la consulta en un árbol de sintaxis, valida los tipos y nombres de tablas en el catálogo del sistema, y el optimizador basado en costos (CBO) evalúa algoritmos físicos de Join (Nested Loops, Hash Join, Merge Join) y escaneo (Seq Scan, Index Scan, Bitmap Scan). La ejecución devuelve tuplas en streaming.",
        "good_practices": "• Usar siempre 'EXPLAIN ANALYZE' para diagnosticar cuellos de botella reales en lugar de adivinar el rendimiento de una consulta.\n• Evitar el antipatrón 'SELECT *' en producción; solicitar únicamente las columnas requeridas para maximizar 'Index-Only Scans' y minimizar tráfico en red y RAM.\n• Utilizar siempre sentencias parametrizadas (Prepared Statements) para neutralizar por completo los ataques de inyección SQL.",
        "example": "-- Consulta con Explain Analyze para verificar uso de índice\nEXPLAIN ANALYZE\nSELECT u.email, COUNT(o.id) as total_pedidos\nFROM usuarios u\nJOIN pedidos o ON u.id = o.usuario_id\nWHERE o.estado = 'COMPLETADO'\nGROUP BY u.email\nHAVING COUNT(o.id) > 5;"
    },
    "http": {
        "title": "HTTP (Hypertext Transfer Protocol)",
        "category": "Redes de datos",
        "what": "Protocolo de capa de aplicación sin estado (stateless) basado en arquitectura cliente-servidor y modelo de petición-respuesta que constituye la base de la comunicación de datos en la World Wide Web y servicios web.",
        "why": "Provee un formato de intercambio universal, legible y extensible por cabeceras para transferir texto, documentos multimedia, APIs RESTful y flujos de eventos entre clientes heterogéneos y servidores globales.",
        "how": "El cliente abre un socket de transporte (TCP puerto 80) y envía un mensaje estructurado en texto claro compuesto por: 1) Línea de petición (Método + URI + Versión), 2) Cabeceras delimitadas por CRLF (Host, User-Agent, Accept, etc.), 3) Línea vacía separadora, y 4) Cuerpo del mensaje opcional. El servidor procesa la petición y responde con una línea de estado (Código numérico + Razón), cabeceras del servidor y cuerpo de respuesta.",
        "good_practices": "• Respetar la semántica de los métodos HTTP: GET, HEAD y OPTIONS deben ser siempre 'seguros' (no modificar estado en el servidor) e idempotentes.\n• Diseñar códigos de estado precisos (200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 429 Too Many Requests, 500 Internal Error).\n• Implementar compresión de transporte (Brotli / Gzip) y cabeceras de caché (Cache-Control, ETag) para reducir consumo de ancho de banda y latencia.",
        "example": "GET /api/v1/usuarios/105 HTTP/1.1\nHost: api.servidor.com\nAccept: application/json\nAuthorization: Bearer eyJhbGciOi...\n\nHTTP/1.1 200 OK\nContent-Type: application/json; charset=utf-8\nCache-Control: private, max-age=300\n\n{\"id\": 105, \"nombre\": \"Carlos\", \"rol\": \"admin\"}"
    },
    "https - tls": {
        "title": "HTTPS & TLS (Transport Layer Security)",
        "category": "Seguridad & Redes",
        "what": "Capa de seguridad criptográfica montada entre la capa de transporte (TCP) y la capa de aplicación (HTTP) que garantiza confidencialidad (cifrado), integridad (detección de manipulación) y autenticación (identidad del servidor validada).",
        "why": "Protege a los usuarios y sistemas frente a ataques de intermediario (Man-In-The-Middle / eavesdropping), robo de contraseñas, suplantación de identidad (spoofing) y manipulación de datos en tránsito a través de redes públicas o no confiables.",
        "how": "1. TLS Handshake: El cliente y servidor negocian la versión de TLS (TLS 1.3 recomendado) y el conjunto de cifrado (Cipher Suite). 2. Autenticación: El servidor presenta su certificado X.509 firmado por una Autoridad de Certificación (CA) de confianza del sistema operativo. 3. Intercambio de claves: Mediante Diffie-Hellman efímero de curvas elípticas (ECDHE), ambos lados generan una clave simétrica compartida sin transmitirla por el cable. 4. Cifrado simétrico: Todo el tráfico subsiguiente viaja protegido con cifrado simétrico de alta velocidad (AES-256-GCM o ChaCha20-Poly1305).",
        "good_practices": "• Deshabilitar versiones obsoletas e inseguras de SSL 2.0/3.0 y TLS 1.0/1.1 en los servidores y balanceadores.\n• Implementar la cabecera HSTS (HTTP Strict Transport Security) con directiva 'preload' para forzar a los navegadores a conectarse exclusivamente mediante HTTPS.\n• Automatizar la renovación de certificados TLS usando ACME (Let's Encrypt / Certbot) para evitar interrupciones de servicio por expiración de certificados.",
        "example": "# Configuración Nginx moderna para TLS 1.3\nssl_protocols TLSv1.2 TLSv1.3;\nssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;\nssl_prefer_server_ciphers off;\nadd_header Strict-Transport-Security \"max-age=63072000; includeSubDomains; preload\" always;"
    },
    "jwt": {
        "title": "JWT (JSON Web Token)",
        "category": "Seguridad & Autenticación",
        "what": "Estándar abierto compacto y autónomo (RFC 7519) para transmitir información segura entre partes en formato de objeto JSON, validado mediante una firma digital criptográfica.",
        "why": "Habilita la autenticación sin estado (stateless) en arquitecturas modernas y microservicios. Al contener en sí mismo los 'claims' del usuario (roles, permisos, expiración), los servidores no necesitan consultar una base de datos o sesión centralizada en cada petición.",
        "how": "Está compuesto por tres fragmentos codificados en Base64URL separados por puntos: 1) Header (tipo de token y algoritmo de firma, ej. HS256 o RS256), 2) Payload (los datos y declaraciones públicas o privadas, como 'sub', 'exp', 'iss'), y 3) Signature (el hash criptográfico del Header + Payload calculado con una clave secreta o privada). Cuando llega una petición, el servidor decodifica el token y valida matemáticamente la firma.",
        "good_practices": "• Usar tiempos de expiración cortos (Access Token de 5 a 15 minutos) combinados con Refresh Tokens rotativos almacenados de forma segura.\n• En arquitecturas distribuidas, preferir firmas asimétricas (RS256 o EdDSA): el servicio de autenticación firma con la clave privada y todos los microservicios validan con la clave pública.\n• NUNCA incluir secretos, contraseñas ni datos sensibles en el payload, ya que Base64URL se puede decodificar públicamente por cualquiera.",
        "example": "# Estructura del token:\n# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTYiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NjQwODAwMDB9.s8dF...\n\n# Validación en backend:\nTokenPayload = decode_token(jwt_string, public_key, algorithms=[\"RS256\"])\nif TokenPayload.exp < current_timestamp():\n    raise TokenExpiredException()"
    },
    "dto": {
        "title": "DTO (Data Transfer Object)",
        "category": "Arquitectura y Diseño",
        "what": "Patrón de diseño estructural que encapsula un conjunto de datos para transportarlos entre procesos, capas de una aplicación o a través de la red, reduciendo el número de llamadas y desacoplando la lógica interna del contrato externo.",
        "why": "Previene la fuga accidental de modelos de base de datos a clientes externos (vulnerabilidad de Mass Assignment), reduce el sobrecoste de red al enviar únicamente los campos necesarios y actúa como una barrera estricta de validación de tipos.",
        "how": "Se modela como una estructura de datos inmutable (clase, dataclass, struct o record) sin lógica de negocio. En el punto de entrada de la API (controlador), la carga útil recibida (JSON) se deserializa y valida contra el esquema del DTO. Si cumple las reglas de formato, se transforma (mediante un Mapper) a una Entidad de Dominio interna.",
        "good_practices": "• Mantener los DTOs completamente libres de dependencias de frameworks de persistencia o bases de datos (no acoplarlos a ORMs).\n• Diseñar DTOs específicos de entrada (CreateUserRequestDTO) separados de los DTOs de salida (UserResponseDTO).\n• Emplear librerías de validación declarativa basadas en tipos (ej. Pydantic en Python, Zod en TypeScript, Bean Validation en Java).",
        "example": "# DTO con validación estricta en Python / Pydantic\nclass CreateUserRequestDTO(BaseModel):\n    username: str = Field(..., min_length=3, max_length=50)\n    email: EmailStr\n    age: int = Field(..., ge=18, le=120)\n    role: Literal[\"reader\", \"editor\"]"
    },
    "middleware": {
        "title": "Middleware — Pipeline de Procesamiento en Cadena",
        "category": "Arquitectura y Backend",
        "what": "Capa intermedia de software situada en el flujo de ejecución entre la recepción de una petición HTTP y el manejador final del controlador de negocio, o entre componentes de un sistema distribuido.",
        "why": "Permite resolver preocupaciones transversales (cross-cutting concerns) —como autenticación, logging, métricas, compresión, rate limiting y CORS— en un solo lugar reutilizable, sin ensuciar la lógica de negocio.",
        "how": "Implementa el patrón de diseño Chain of Responsibility. Cada middleware recibe la petición, puede inspeccionarla o mutarla, decide si continuar pasando el control al siguiente eslabón mediante una llamada 'next()' o abortar el flujo inmediatamente devolviendo una respuesta de error. Cuando el controlador final termina, la respuesta viaja de vuelta a través de la misma cadena en orden inverso.",
        "good_practices": "• Cuidar rigurosamente el orden de registro de los middlewares: middlewares de pánico/recuperación y logs deben ir primero; autenticación antes de autorización.\n• Evitar bloqueos I/O síncronos dentro de un middleware para no estrangular el rendimiento global del servidor.\n• Utilizar middlewares para inyectar identificadores únicos de correlación (Correlation ID / Request ID) en el contexto de cada petición.",
        "example": "# Middleware HTTP en Go\nfunc CorrelationIDMiddleware(next http.Handler) http.Handler {\n    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {\n        reqID := r.Header.Get(\"X-Request-ID\")\n        if reqID == \"\" { reqID = uuid.NewString() }\n        ctx := context.WithValue(r.Context(), \"RequestID\", reqID)\n        w.Header().Set(\"X-Request-ID\", reqID)\n        next.ServeHTTP(w, r.WithContext(ctx))\n    })\n}"
    },
    "event loop": {
        "title": "Event Loop (Bucle de Eventos e I/O Asíncrono)",
        "category": "Runtimes y Sistemas Operativos",
        "what": "Mecanismo arquitectónico de ejecución concurrente de un solo hilo (o hilo principal) que despacha eventos, procesa tareas y coordina operaciones de entrada/salida no bloqueantes.",
        "why": "Permite a entornos como Node.js, Python asyncio o Chromium manejar decenas de miles de conexiones de red concurrentes con una huella de memoria insignificante, superando el modelo clásico de 'un hilo por conexión' que colapsa por consumo de RAM y context switches.",
        "how": "El bucle ejecuta continuamente fases secuenciales: 1) Procesa código síncrono en el Call Stack, 2) Delega operaciones de red y disco al kernel del sistema operativo mediante APIs no bloqueantes (epoll en Linux, kqueue en macOS, IOCP en Windows) o a un pool de hilos de fondo (libuv), 3) Cuando una operación I/O finaliza, su callback se encola en la cola de tareas (Task Queue / Microtask Queue), y 4) Cuando el Call Stack queda vacío, el bucle toma el primer callback y lo ejecuta.",
        "good_practices": "• NUNCA bloquear el hilo principal con cálculos matemáticos intensivos o algoritmos síncronos pesados (ej. cifrado masivo de claves); delegar esas cargas a Worker Threads.\n• Evitar el anidamiento excesivo de callbacks ('callback hell') utilizando siempre async/await con gestión de errores tipada.\n• Entender la prioridad de microtareas (Promises) frente a macrotareas (setTimeout, I/O): las microtareas se vacían por completo antes del siguiente tick del loop.",
        "example": "// Demostración de fases en Node.js Event Loop\nconsole.log('1: Síncrono');\nsetTimeout(() => console.log('4: Macrotarea (Timer)'), 0);\nPromise.resolve().then(() => console.log('3: Microtarea (Promesa)'));\nconsole.log('2: Síncrono');\n// Salida ordenada: 1, 2, 3, 4"
    },
    "solid": {
        "title": "Principios SOLID de Diseño Orientado a Objetos",
        "category": "Principios de Ingeniería de Software",
        "what": "Acrónimo mnemotécnico de cinco principios esenciales de diseño de software promovidos por Robert C. Martin para construir aplicaciones robustas, comprensibles y fáciles de mantener.",
        "why": "Elimina los tres mayores síntomas del código defectuoso: Rigidez (difícil de cambiar), Fragilidad (un cambio rompe partes inesperadas) e Inmovilidad (imposible de reutilizar módulos en otros proyectos).",
        "how": "1. S (Single Responsibility): Una clase debe tener una única razón para cambiar.\n2. O (Open/Closed): Las entidades deben estar abiertas para su extensión, pero cerradas para su modificación.\n3. L (Liskov Substitution): Los subtipos deben poder sustituir a sus tipos base sin alterar la corrección del programa.\n4. I (Interface Segregation): Los clientes no deben ser forzados a depender de interfaces o métodos que no utilizan.\n5. D (Dependency Inversion): Los módulos de alto nivel no deben depender de módulos de bajo nivel; ambos deben depender de abstracciones.",
        "good_practices": "• No sobre-ingenierizar: aplicar SOLID cuando el dominio evoluciona, no como una religión dogmática en scripts triviales.\n• Usar composición sobre herencia para cumplir con OCP y LSP de forma natural.\n• Separar interfaces gigantescas en pequeñas interfaces específicas enfocadas en un solo rol.",
        "example": "# Cumplimiento de Dependency Inversion y Single Responsibility\nclass EmailNotifier(Protocol):\n    def send(self, recipient: str, msg: str) -> None: ...\n\nclass UserRegistrationService:\n    def __init__(self, notifier: EmailNotifier, repo: UserRepository):\n        self.notifier = notifier\n        self.repo = repo\n    \n    def register(self, user_data: UserDTO) -> None:\n        # Lógica de registro desacoplada de la implementación del correo\n        pass"
    },
    "kubernetes": {
        "title": "Kubernetes (K8s) — Orquestador de Contenedores a Escala",
        "category": "Contenerización y Orquestación",
        "what": "Sistema de código abierto de grado de producción diseñado para automatizar el despliegue, escalado, balanceo de carga y gestión del ciclo de vida de aplicaciones contenedorizadas en clústeres de servidores distribuidos.",
        "why": "Gestionar decenas o miles de contenedores Docker manualmente en múltiples servidores físicos o virtuales es inviable. Kubernetes provee una capa de abstracción declarativa que garantiza que el estado real del clúster coincida siempre con el estado deseado por los ingenieros.",
        "how": "Arquitectura dividida en Control Plane (API Server, etcd para almacenamiento de estado, Kube-Scheduler para asignación de nodos y Kube-Controller-Manager) y Worker Nodes (Kubelet como agente de nodo, Kube-Proxy para reglas de red iptables/IPVS y el Container Runtime Interface como containerd). Funciona mediante bucles continuos de reconciliación: si un contenedor muere, Kubelet lo reinicia automáticamente en milisegundos.",
        "good_practices": "• Definir siempre 'requests' y 'limits' de CPU y memoria en cada contenedor para evitar que un Pod hambriento mate a otros en el mismo nodo (OOMKilled).\n• Configurar liveness y readiness probes inteligentes para asegurar que el tráfico solo llegue a Pods que hayan completado su arranque interno.\n• Desplegar las aplicaciones con PodDisruptionBudgets (PDB) y múltiples réplicas distribuidas entre distintas zonas de disponibilidad.",
        "example": "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: backend-api\nspec:\n  replicas: 3\n  selector:\n    matchLabels:\n      app: api\n  template:\n    metadata:\n      labels:\n        app: api\n    spec:\n      containers:\n      - name: api\n        image: mi-registro.com/api:v1.4\n        resources:\n          requests:\n            memory: \"128Mi\"\n            cpu: \"100m\"\n          limits:\n            memory: \"512Mi\"\n            cpu: \"500m\""
    },
    "grpc": {
        "title": "gRPC — Marco de Llamadas a Procedimiento Remoto de Alto Rendimiento",
        "category": "APIs e Integraciones de Red",
        "what": "Framework open-source de comunicación RPC universal de baja latencia desarrollado originalmente por Google, basado en contratos estrictos definidos mediante Protocol Buffers y transporte sobre HTTP/2.",
        "why": "En arquitecturas de microservicios masivas, la sobrecarga del formato JSON basado en texto y peticiones HTTP/1.1 satura la red y consume demasiada CPU en parsing. gRPC ofrece serialización binaria ultra-compacta y streaming bidireccional.",
        "how": "Los servicios y mensajes se declaran en archivos '.proto'. El compilador 'protoc' genera automáticamente código cliente y servidor fuertemente tipado en más de 10 lenguajes. El transporte utiliza HTTP/2 nativo, permitiendo multiplexación de múltiples llamadas concurrentes en una única conexión TCP persistente, compresión de cabeceras HPACK y soporte para streaming continuo cliente, servidor o bidireccional.",
        "good_practices": "• Mantener compatibilidad hacia atrás en los contratos '.proto': nunca reutilizar ni cambiar el número identificador numérico de un campo existente.\n• Utilizar interceptores (Interceptors) para centralizar logging, métricas de latencia y propagación de tokens de autenticación o metadatos de rastreo.\n• Balancear la carga a nivel de capa 7 (con Envoy o Service Mesh), ya que los balanceadores tradicionales de capa 4 fallan al persistir la conexión HTTP/2 a un solo nodo.",
        "example": "syntax = \"proto3\";\npackage pagos;\n\nservice ServicioPagos {\n  rpc ProcesarPago (SolicitudPago) returns (RespuestaPago);\n}\n\nmessage SolicitudPago {\n  string transaccion_id = 1;\n  double monto = 2;\n  string moneda = 3;\n}\n\nmessage RespuestaPago {\n  bool exito = 1;\n  string codigo_autorizacion = 2;\n}"
    },
    "rag": {
        "title": "RAG (Retrieval-Augmented Generation)",
        "category": "Inteligencia Artificial y Sistemas Agénticos",
        "what": "Patrón arquitectónico de IA que combina modelos de lenguaje generativo (LLMs) con sistemas de recuperación de información externos para responder consultas utilizando datos privados, actualizados y fidedignos sin necesidad de reentrenar el modelo.",
        "why": "Los LLMs sufren de alucinaciones y su conocimiento está limitado a la fecha de corte de su entrenamiento. RAG ancla las respuestas del modelo en los documentos reales de la empresa, garantizando trazabilidad y confidencialidad con permisos de acceso.",
        "how": "1. Ingesta: Los documentos de la organización se fragmentan (Chunking), se convierten a vectores multidimensionales mediante un modelo de Embedding (ej. text-embedding-3) y se indexan en una base de datos vectorial (pgvector, Qdrant, Pinecone).\n2. Recuperación: Cuando el usuario hace una pregunta, se calcula el vector de la consulta y se buscan los fragmentos más cercanos por similitud del coseno (algoritmo HNSW).\n3. Generación: Se ensambla un prompt enriquecido que contiene la pregunta original más los fragmentos recuperados como contexto de referencia para que el LLM sintetice la respuesta final.",
        "good_practices": "• Invertir tiempo en la estrategia de fragmentación (Semantic Chunking) para no partir oraciones ni perder tablas o metadatos clave.\n• Implementar un paso de 'Re-ranking' (Cross-Encoder) tras la recuperación vectorial inicial para filtrar fragmentos irrelevantes antes de enviarlos al LLM.\n• Exigir al LLM en el system prompt citar explícitamente las fuentes y abstenerse de responder si el contexto no contiene la información requerida.",
        "example": "# Flujo conceptual de RAG\nquery_vector = embed_model.embed(user_question)\nrelevant_chunks = vector_db.search_knn(query_vector, k=4)\ncontext_text = \"\\n---\\n\".join([c.text for c in relevant_chunks])\n\nprompt = f\"Responde basándote ÚNICAMENTE en el siguiente contexto:\\n{context_text}\\nPregunta: {user_question}\"\nfinal_answer = llm.generate(prompt)"
    },
    "mcp": {
        "title": "MCP (Model Context Protocol)",
        "category": "Inteligencia Artificial y Protocolos Agénticos",
        "what": "Protocolo abierto y estandarizado desarrollado por Anthropic para conectar modelos de inteligencia artificial y entornos de desarrollo de forma segura y bidireccional con fuentes de datos externas, herramientas locales y servicios en la nube.",
        "why": "Antes de MCP, cada herramienta, IDE o agente requería integraciones ad-hoc y propietarias con bases de datos, APIs de GitHub o repositorios locales. MCP actúa como el 'USB-C de la IA', permitiendo que cualquier cliente consuma cualquier servidor de herramientas bajo un mismo estándar.",
        "how": "Sigue una arquitectura cliente-servidor basada en JSON-RPC 2.0 sobre transportes estándar (stdio para procesos locales o Server-Sent Events / SSE sobre HTTP para remotos). El protocolo expone tres primitivas esenciales: 1) Tools (funciones ejecutables por el modelo para provocar efectos secundarios o consultar APIs), 2) Resources (datos estructurados y lectura de archivos pasivos), y 3) Prompts (plantillas reutilizables preconfiguradas).",
        "good_practices": "• Aplicar el principio de menor privilegio en los servidores MCP: conceder permisos de solo lectura a bases de datos y archivos sensibles a menos que se requiera explícitamente escritura.\n• Implementar confirmación humana obligatoria ('Human-in-the-loop') para herramientas de alto impacto destructivo (ej. borrar tablas, desplegar a producción, enviar dinero).\n• Documentar con suma precisión en el esquema JSON de cada herramienta su descripción y parámetros para guiar el razonamiento del modelo sin confusiones.",
        "example": "{\n  \"jsonrpc\": \"2.0\",\n  \"method\": \"tools/call\",\n  \"params\": {\n    \"name\": \"ejecutar_consulta_sql\",\n    \"arguments\": {\n      \"query\": \"SELECT id, nombre FROM clientes WHERE saldo > 1000 LIMIT 5;\"\n    }\n  },\n  \"id\": 42\n}"
    }
}

def generate_technical_card(name, folder, meta, node_data=None):
    """
    Genera el HTML estructurado y exhaustivo de una tecnología.
    """
    clean_name = name.strip()
    key = clean_name.lower()
    
    # Si tenemos ficha especializada profunda
    for k, v in DEEP_CONCEPTS.items():
        if k == key or k in key:
            return render_custom_card(v, clean_name, folder, meta)
            
    # Si la nota original tiene una guía completa en markdown (ej. Git, Docker, etc.)
    if node_data and node_data.get('is_guia') and len(node_data.get('body', '')) > 200:
        return render_markdown_guide_card(clean_name, folder, meta, node_data)
        
    # Si es un concepto estándar, generamos una ficha técnica con rigor de ingeniería
    return render_standard_tech_card(clean_name, folder, meta, node_data)

def render_custom_card(c, name, folder, meta):
    return f"""
    <div class="tech-card card-deep">
        <div class="card-header">
            <div class="title-wrap">
                <span class="tech-badge badge-deep">Profundidad Técnica</span>
                <span class="tech-badge badge-category">{html.escape(c.get('category', meta.get('title', folder)))}</span>
                <h3 class="tech-title">{html.escape(c.get('title', name))}</h3>
            </div>
        </div>
        
        <div class="card-grid">
            <div class="card-block block-what">
                <span class="block-label">¿QUÉ ES EXACTAMENTE?</span>
                <p>{html.escape(c['what'])}</p>
            </div>
            <div class="card-block block-why">
                <span class="block-label">¿PARA QUÉ SIRVE Y QUÉ PROBLEMA RESUELVE?</span>
                <p>{html.escape(c['why'])}</p>
            </div>
        </div>
        
        <div class="card-block block-how">
            <span class="block-label">¿CÓMO FUNCIONA TÉCNICAMENTE (MECANISMO INTERNO)?</span>
            <p>{html.escape(c['how']).replace(chr(10), '<br>')}</p>
        </div>
        
        <div class="card-grid">
            <div class="card-block block-practices">
                <span class="block-label">BUENAS PRÁCTICAS Y ERRORES DE PRODUCCIÓN</span>
                <p>{html.escape(c['good_practices']).replace(chr(10), '<br>')}</p>
            </div>
            <div class="card-block block-example">
                <span class="block-label">CÓDIGO / FLUJO / EJEMPLO CLAVE</span>
                <pre><code>{html.escape(c.get('example', ''))}</code></pre>
            </div>
        </div>
    </div>
    """

def render_markdown_guide_card(name, folder, meta, node_data):
    body = node_data.get('body', '')
    # Tomar secciones iniciales más relevantes
    sections = body.split('## ')
    summary_html = []
    for s in sections[1:5]:
        lines = s.strip().split('\n')
        title = lines[0].strip()
        content = '\n'.join(lines[1:8]).strip()
        if content:
            summary_html.append(f"<div class='guide-section'><strong>{html.escape(title)}:</strong><p>{html.escape(content[:400])}...</p></div>")
            
    summary_str = ''.join(summary_html) if summary_html else f"<p>{html.escape(body[:500])}...</p>"
    
    return f"""
    <div class="tech-card card-guide">
        <div class="card-header">
            <div class="title-wrap">
                <span class="tech-badge badge-star">⭐ Núcleo Dominar</span>
                <span class="tech-badge badge-category">{html.escape(meta.get('title', folder))}</span>
                <h3 class="tech-title">{html.escape(name)} — Guía Maestra</h3>
            </div>
        </div>
        <div class="card-block block-what">
            <span class="block-label">RESUMEN TÉCNICO Y FUNDAMENTOS DE PRODUCCIÓN</span>
            {summary_str}
        </div>
    </div>
    """

def render_standard_tech_card(name, folder, meta, node_data):
    rels = node_data.get('relacionados', []) if node_data else []
    rel_html = ", ".join([f"<span class='rel-tag'>{html.escape(r)}</span>" for r in rels[:5]]) if rels else "Concepto transversal"
    
    # Deducción inteligente según nombre y carpeta
    what_desc = f"Componente, protocolo o estructura de software perteneciente al dominio de {meta.get('title', folder)}."
    why_desc = f"Resuelve la necesidad de estandarizar, optimizar o gobernar el comportamiento de los sistemas dentro del área de {meta.get('title', folder)}."
    how_desc = f"Se integra en el ciclo de vida del software mediante interfaces definidas, algoritmos de procesamiento y contratos de ejecución acordes a las especificaciones de {folder}."
    
    # Ajustes temáticos por palabras clave
    ln = name.lower()
    if any(k in ln for k in ['algoritmo', 'sort', 'search', 'árbol', 'tree', 'grafo', 'hash', 'cola', 'pila', 'heap']):
        what_desc = f"Estructura o procedimiento algorítmico determinista diseñado para manipular y organizar colecciones de datos en memoria."
        why_desc = "Garantiza cotas de rendimiento asintótico (Big O) en tiempo y espacio de cómputo, evitando cuellos de botella en alta concurrencia."
        how_desc = "Asigna nodos en memoria (punteros contiguos o dispersos) y ejecuta recorridos y particiones mediante punteros o llamadas recursivas."
    elif any(k in ln for k in ['test', 'prueba', 'mock', 'assert', 'tdd', 'qa']):
        what_desc = "Mecanismo o patrón de aseguramiento de calidad y verificación continua del software."
        why_desc = "Garantiza que los cambios futuros no rompan contratos preexistentes (regresión) y documenta de forma viva el comportamiento del sistema."
        how_desc = "Ejecuta escenarios controlados, inyecta dobles de prueba (fakes/stubs) y compara los valores retornados contra criterios de aceptación matemáticos."
    elif any(k in ln for k in ['cifrado', 'auth', 'seguridad', 'token', 'owasp', 'vulnerabilidad', 'hash']):
        what_desc = "Mecanismo criptográfico o control defensivo para salvaguardar la tríada CIA (Confidencialidad, Integridad y Disponibilidad)."
        why_desc = "Neutraliza vectores de ataque comunes, robo de sesiones, escalada de privilegios y fuga de datos sensibles en reposo o tránsito."
        how_desc = "Aplica funciones unidireccionales (hashing con salt), intercambio de secretos asimétricos o listas de control de acceso (ACL/RBAC) en el flujo de ejecución."
        
    return f"""
    <div class="tech-card card-standard">
        <div class="card-header">
            <div class="title-wrap">
                <span class="tech-badge badge-standard">Tecnología / Concepto</span>
                <span class="tech-badge badge-category">{html.escape(meta.get('title', folder))}</span>
                <h3 class="tech-title">{html.escape(name)}</h3>
            </div>
            <div class="card-rels">
                <span class="rels-title">Conexiones:</span> {rel_html}
            </div>
        </div>
        
        <div class="card-grid">
            <div class="card-block block-what">
                <span class="block-label">¿QUÉ ES?</span>
                <p>{html.escape(what_desc)}</p>
            </div>
            <div class="card-block block-why">
                <span class="block-label">¿PARA QUÉ SIRVE?</span>
                <p>{html.escape(why_desc)}</p>
            </div>
        </div>
        
        <div class="card-block block-how">
            <span class="block-label">¿CÓMO FUNCIONA E INTERACTÚA CON EL SISTEMA?</span>
            <p>{html.escape(how_desc)}</p>
        </div>
    </div>
    """
