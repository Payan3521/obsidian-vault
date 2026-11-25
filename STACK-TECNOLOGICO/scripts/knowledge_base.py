# -*- coding: utf-8 -*-
"""
Mapeo exhaustivo de carpetas y conocimiento técnico estructurado.
Define el propósito de ingeniería de cada carpeta y fichas de profundidad técnica.
"""

FOLDER_METADATA = {
    "fundamentos-de-programación": {
        "title": "Fundamentos de Programación",
        "semester": "Semestre I",
        "role": "Los cimientos del pensamiento computacional y construcción de lógica determinista.",
        "why": "Sin una base sólida de control de flujo, estructuras de control, tipos de datos y abstracciones de POO, cualquier código colapsa en deuda técnica antes de escalar.",
        "internal_mechanics": "Los compiladores e intérpretes traducen expresiones algebraicas y lógicas en tablas de símbolos, árboles sintácticos (AST) y secuencias de instrucciones en bytecode o código máquina ejecutable en registros de CPU."
    },
    "principios-de-ingeniería-de-software": {
        "title": "Principios de Ingeniería de Software",
        "semester": "Semestre I",
        "role": "Directrices de diseño para código mantenible, desacoplado y extensible.",
        "why": "El software pasa el 90% de su ciclo de vida en mantenimiento. Principios como SOLID, DRY, KISS y YAGNI minimizan el coste de cambio y previenen el código espagueti.",
        "internal_mechanics": "Favorece la inyección de dependencias, la inversión de control (IoC), la segregación de interfaces y la responsabilidad única, permitiendo testear y cambiar componentes aisladamente sin efectos colaterales."
    },
    "matemáticas-i": {
        "title": "Matemáticas I (Cálculo Diferencial e Integral)",
        "semester": "Semestre I",
        "role": "Modelado de tasas de cambio continuo, optimización y límites.",
        "why": "Imprescindible para comprender gradientes en algoritmos de machine learning, análisis de rendimiento asintótico y modelos de latencia.",
        "internal_mechanics": "El cálculo diferencial analiza pendientes infinitesimales (derivadas) que permiten a los optimizadores (como SGD o Adam) converger hacia mínimos globales o locales en funciones de pérdida complejas."
    },
    "física-i-mecánica": {
        "title": "Física I — Mecánica Clásica",
        "semester": "Semestre I",
        "role": "Leyes del movimiento, energía, dinámica de sistemas y simulación física.",
        "why": "Fundamento indispensable para desarrollo de motores de videojuegos, gráficos por computadora (CGI), robótica, cinemática y simuladores industriales.",
        "internal_mechanics": "Aplica leyes de Newton, conservación de energía y momento lineal mediante integradores numéricos discretos (Euler, Verlet, Runge-Kutta) en bucles de simulación (game loops)."
    },
    "lenguajes-runtimes-y-build": {
        "title": "Lenguajes, Runtimes y Herramientas de Build",
        "semester": "Semestre II",
        "role": "Ecosistemas de ejecución, máquinas virtuales y empaquetado de código.",
        "why": "Elegir el lenguaje y runtime correcto determina el rendimiento por hilo, latencia de garbage collection (GC), huella de memoria y velocidad de despliegue.",
        "internal_mechanics": "Compara runtimes basados en JIT (V8, JVM, CLR), intérpretes con GIL (Python CPython) y lenguajes compilados nativos sin recolector de basura (Rust, Go, C++)."
    },
    "álgebra-lineal": {
        "title": "Álgebra Lineal",
        "semester": "Semestre II",
        "role": "Transformaciones vectoriales, matrices y espacios multidimensionales.",
        "why": "Es el lenguaje matemático del Deep Learning, embeddings de IA, RAG, procesamiento de señales y renderizado 3D.",
        "internal_mechanics": "Multiplicaciones matriciales optimizadas (BLAS, cuBLAS en GPUs) permiten calcular atenciones en transformers y transformaciones afines en tiempo real."
    },
    "matemáticas-ii": {
        "title": "Matemáticas II (Cálculo Multivariable)",
        "semester": "Semestre II",
        "role": "Cálculo en espacios de múltiples dimensiones, derivadas parciales y gradientes.",
        "why": "La base sobre la que se fundamenta la retropropagación (backpropagation) en redes neuronales y la optimización en espacios vectoriales masivos.",
        "internal_mechanics": "La matriz Jacobiana y Hessiana evalúan derivadas parciales de primer y segundo orden para optimizar superficies hiperdimensionales en arquitecturas de IA modernas."
    },
    "física-ii-electromagnetismo": {
        "title": "Física II — Electromagnetismo",
        "semester": "Semestre II",
        "role": "Circuitos, señales eléctricas, propagación de ondas y semiconductores.",
        "why": "Permite entender cómo funciona el hardware físico, la transmisión óptica en fibra de telecomunicaciones y el comportamiento de transistores en silicio.",
        "internal_mechanics": "Ecuaciones de Maxwell y modulación de pulsos electromagnéticos que rigen la capacidad de canal (Teorema de Shannon-Hartley) en redes de alta velocidad."
    },
    "ética-y-legalidad-profesional": {
        "title": "Ética, Legalidad y Cumplimiento Normativo",
        "semester": "Semestre II",
        "role": "Gobernanza de software, privacidad de datos, licencias y accesibilidad.",
        "why": "Un sistema seguro y funcional fracasa comercial y legalmente si viola GDPR, HIPAA, SOC2 o directrices de accesibilidad (WCAG/axe).",
        "internal_mechanics": "Establece marcos de gobernanza, auditoría continua de código abierto, contratos de procesamiento de datos (DPA) y políticas de privacidad por diseño."
    },
    "estructuras-de-datos-y-algoritmos": {
        "title": "Estructuras de Datos y Algoritmos (DSA)",
        "semester": "Semestre III",
        "role": "Organización eficiente de memoria y algoritmos de alta complejidad.",
        "why": "La diferencia entre un sistema que procesa 1 millón de peticiones en milisegundos o se congela por consumo O(N²) de CPU radica en las estructuras de datos escogidas.",
        "internal_mechanics": "B-Trees y LSM-Trees en motores de bases de datos, Skip Lists en Redis, Hash tables con resolución de colisiones y algoritmos de búsqueda grafos (Dijkstra, A*)."
    },
    "desarrollo-de-software": {
        "title": "Desarrollo de Software y Ciclo de Vida (SDLC)",
        "semester": "Semestre III",
        "role": "Ingeniería de requerimientos, metodologías ágiles y gestión de deuda técnica.",
        "why": "Construir el producto equivocado o sin especificaciones precisas cuesta 10x más corregirlo en producción que en fase de diseño.",
        "internal_mechanics": "Transforma historias de usuario y requerimientos funcionales/no funcionales en criterios de aceptación verificables mediante BDD y TDD."
    },
    "matemáticas-iii": {
        "title": "Matemáticas III (Ecuaciones Diferenciales y Series)",
        "semester": "Semestre III",
        "role": "Modelado de sistemas dinámicos que cambian en el tiempo.",
        "why": "Vital en procesamiento de audio digital, visión computacional, finanzas cuantitativas y modelos predictivos de tráfico de red.",
        "internal_mechanics": "Series de Fourier y transformadas de Laplace que descomponen señales complejas en ondas armónicas procesables algorítmicamente."
    },
    "diseño-de-interfaces-de-usuario": {
        "title": "Diseño de Interfaces de Usuario (UI/UX)",
        "semester": "Semestre III",
        "role": "Diseño centrado en el usuario, Design Systems, wireframing y accesibilidad visual.",
        "why": "Una arquitectura impecable fracasa si el usuario no puede entender ni operar intuitivamente el producto.",
        "internal_mechanics": "Jerarquía visual, patrones F y Z de escaneo ocular, tokens de diseño sincronizados entre Figma y código frontend (CSS/Tailwind) para consistencia total."
    },
    "estadística-y-probabilidad": {
        "title": "Estadística y Probabilidad",
        "semester": "Semestre III",
        "role": "Toma de decisiones bajo incertidumbre, muestreo y distribuciones.",
        "why": "Gobierna los A/B testings, la evaluación de percentiles de latencia (p95, p99), detección de anomalías en observabilidad y modelos estocásticos de IA.",
        "internal_mechanics": "Teorema de Bayes, distribución de Poisson para llegada de peticiones en colas y test de hipótesis para validar cambios en producción con rigor matemático."
    },
    "bases-de-datos": {
        "title": "Bases de Datos (SQL, NoSQL, NewSQL)",
        "semester": "Semestre IV",
        "role": "Persistencia de estado fiable, transaccionalidad y modelos de datos.",
        "why": "Los datos son el activo más valioso de cualquier negocio; una pérdida de consistencia transaccional o corrupción de datos destruye empresas.",
        "internal_mechanics": "Garantías ACID mediante Write-Ahead Logging (WAL) y aislamiento MVCC en relacionales, particionamiento horizontal sharding y teoremas PACELC en NoSQL distribuidas."
    },
    "matemáticas-iv": {
        "title": "Matemáticas IV (Análisis Numérico y Optimización)",
        "semester": "Semestre IV",
        "role": "Algoritmos para resolver problemas matemáticos continuos mediante aproximaciones discretas.",
        "why": "Las computadoras tienen precisión finita de coma flotante (IEEE 754). El análisis numérico previene errores catastróficos de redondeo y divergencia.",
        "internal_mechanics": "Método de Newton-Raphson, descomposición LU/QR y optimización convexa con restricciones de Karush-Kuhn-Tucker (KKT)."
    },
    "construcción-de-app-empresariales": {
        "title": "Construcción de Aplicaciones Empresariales",
        "semester": "Semestre IV",
        "role": "Arquitectura de software empresarial, integración de procesos B2B y resiliencia.",
        "why": "Las aplicaciones corporativas requieren operar 24/7 con alta auditoría, tolerancia a fallos, soporte de multi-inquilino (multi-tenant) y migración sin downtime.",
        "internal_mechanics": "Patrones de despliegue continuo con Feature Flags, Circuit Breakers, Outbox Pattern y orquestación de transacciones distribuidas con Saga."
    },
    "ingeniería-de-software-i": {
        "title": "Ingeniería de Software I",
        "semester": "Semestre V",
        "role": "Especificación formal, análisis de arquitectura y diseño detallado.",
        "why": "Permite estructurar sistemas de gran escala antes de escribir una sola línea de código, evitando refactorizaciones costosas.",
        "internal_mechanics": "Mapeo de dominios mediante Domain-Driven Design (DDD), definición de Bounded Contexts y modelos conceptuales rigurosos."
    },
    "construcción-de-apps-móviles": {
        "title": "Construcción de Aplicaciones Móviles",
        "semester": "Semestre V",
        "role": "Desarrollo nativo e híbrido para iOS y Android.",
        "why": "Los dispositivos móviles operan con recursos restringidos de batería, CPU y conexiones de red inestables que demandan arquitecturas offline-first.",
        "internal_mechanics": "Runtimes reactivos (React Native, Flutter, Kotlin Multiplatform), sincronización con SQLite local (Room/CoreData) y push notifications mediante APNs/FCM."
    },
    "desarrollo-web": {
        "title": "Desarrollo Web Moderno",
        "semester": "Semestre V",
        "role": "Arquitectura cliente-servidor web, Single Page Apps, Server-Side Rendering y APIs.",
        "why": "La web es la plataforma universal de distribución de software sin fricción de instalación para millones de usuarios simultáneos.",
        "internal_mechanics": "Hydration en frameworks SSR (Next.js/Remix), Virtual DOM, Service Workers para Progressive Web Apps (PWA) y optimización de Core Web Vitals."
    },
    "sistemas-operativos-lo-que-deberías-saber-hoy": {
        "title": "Sistemas Operativos (Internals y Producción)",
        "semester": "Semestre VI",
        "role": "Gestión de memoria virtual, planificación de CPU, llamadas al sistema (syscalls) y Linux internals.",
        "why": "Todo el código de alto nivel corre en un sistema operativo. Quien no entiende I/O no bloqueante, context switching y memoria virtual no puede optimizar un backend de alto rendimiento.",
        "internal_mechanics": "Syscalls (epoll, io_uring), paginación y TLB, cgroups y namespaces que dan vida a Docker, señales POSIX y subsistema de archivos en Linux."
    },
    "redes-de-datos-vista-práctica-y-moderna": {
        "title": "Redes de Datos (Práctica Moderna y Producción)",
        "semester": "Semestre VI",
        "role": "Protocolos de comunicación de capas 2 a 7, enrutamiento, seguridad perimetral y transporte.",
        "why": "En la era de microservicios y cloud, la red no es un cable: es un componente activo del software sujeto a latencias, caídas y ataques.",
        "internal_mechanics": "Three-way handshake TCP, multiplexación HTTP/2 y HTTP/3 sobre QUIC (UDP), resolución DNS jerárquica, políticas CORS en navegadores y mTLS para Zero Trust."
    },
    "ingeniería-de-software-ii": {
        "title": "Ingeniería de Software II",
        "semester": "Semestre VI",
        "role": "Aseguramiento de calidad formal, métricas de código y mantenimiento de evolución.",
        "why": "Garantiza que el software continúe siendo operable, seguro y mantenible a medida que crece el equipo de ingeniería.",
        "internal_mechanics": "Métricas de complejidad ciclomática de McCabe, cobertura de ramas, análisis de impacto de cambios y planes de contingencia tecnológica."
    },
    "matemática-discreta": {
        "title": "Matemática Discreta",
        "semester": "Semestre VI",
        "role": "Lógica proposicional, teoría de conjuntos, grafos y combinatoria.",
        "why": "El hardware y la computación son inherentemente discretos: estados binarios, grafos de dependencias y criptografía de clave pública.",
        "internal_mechanics": "Álgebra booleana en circuitos digitales, árboles de expansión mínima (MST) en topologías de red y relaciones de equivalencia en bases de datos relacionales."
    },
    "sistemas-distribuidos": {
        "title": "Sistemas Distribuidos",
        "semester": "Semestre VII",
        "role": "Consenso, tolerancia a fallos, particionamiento y replicación de datos.",
        "why": "Una sola máquina no puede soportar la carga mundial. Pero distribuir cómputo introduce el problema de relojes asíncronos y fallas parciales.",
        "internal_mechanics": "Teorema CAP, algoritmos de consenso (Raft, Paxos), consistencia eventual, Vector Clocks y modelos de replicación primaria-réplica."
    },
    "infraestructura-de-ti": {
        "title": "Infraestructura de TI y Virtualización",
        "semester": "Semestre VII",
        "role": "Servidores bare-metal, hipervisores, almacenamiento SAN/NAS y topologías de datacenter.",
        "why": "Provee el sustrato físico y virtualizado sobre el que operan las nubes privadas y públicas con alta resiliencia eléctrica y térmica.",
        "internal_mechanics": "Hipervisores Tipo 1 (KVM, ESXi), virtualización de CPU por hardware (Intel VT-x / AMD-V), redes definidas por software (SDN) y almacenamiento por bloques."
    },
    "desarrollo-en-equipo": {
        "title": "Desarrollo en Equipo y Cultura de Ingeniería",
        "semester": "Semestre VII",
        "role": "Flujos de trabajo colaborativos, Code Reviews, post-mortems y liderazgo técnico.",
        "why": "El software complejo es una labor de equipo multidisciplinar. Las fallas de comunicación destruyen proyectos más rápido que los bugs de código.",
        "internal_mechanics": "Trunk-Based Development, ramas efímeras, políticas de protección de ramas, plantillas de PR con checklist de seguridad y cultura 'blameless post-mortem'."
    },
    "simulación": {
        "title": "Simulación y Computación Científica",
        "semester": "Semestre VII",
        "role": "Modelos computacionales de sistemas complejos y métodos de Monte Carlo.",
        "why": "Permite predecir el comportamiento de sistemas caóticos (tráfico urbano, bolsa de valores, aerodinámica) antes de invertir millones en ejecución real.",
        "internal_mechanics": "Generadores de números pseudoaleatorios criptográficamente seguros, simulaciones de eventos discretos (DES) y computación paralela masiva en clústeres."
    },
    "compiladores": {
        "title": "Compiladores y Teoría de Lenguajes",
        "semester": "Semestre VIII",
        "role": "Análisis léxico, sintáctico, semántico, optimización y generación de código binario.",
        "why": "Entender compiladores transforma a un programador de ser un usuario de sintaxis a un verdadero arquitecto que comprende cómo la CPU ejecuta el software.",
        "internal_mechanics": "Autómatas finitos (Lexers), gramáticas libres de contexto (Parsers LL/LR), representación intermedia (IR) como LLVM y asignación de registros de hardware mediante coloración de grafos."
    },
    "temas-avanzados-de-ingeniería-de-software": {
        "title": "Temas Avanzados de Ingeniería de Software",
        "semester": "Semestre VIII",
        "role": "Computación cuántica, arquitecturas serverless, eBPF y frontier computing.",
        "why": "Anticipa la próxima ola tecnológica que reemplazará las arquitecturas actuales en los próximos 5 a 10 años.",
        "internal_mechanics": "Algoritmos cuánticos (Shor, Grover), instrumentación de kernel con eBPF en tiempo de ejecución sin recompilar y arquitecturas WebAssembly (Wasm) en el edge."
    },
    "gestión-de-proyectos-de-ti": {
        "title": "Gestión de Proyectos de TI",
        "semester": "Semestre VIII",
        "role": "Estimación, gestión de riesgos, presupuestos, SLA/SLO y entrega de valor.",
        "why": "Un proyecto técnicamente perfecto que se entrega 2 años tarde o quintuplica el presupuesto quiebra la organización.",
        "internal_mechanics": "Métricas ágiles de flujo (Lead Time, Cycle Time, Throughput), gestión de riesgos cuantitativa y contratos de nivel de servicio vinculantes."
    },
    "control-de-versiones-y-flujo-de-código": {
        "title": "Control de Versiones y Flujo de Código",
        "semester": "Núcleo Profesional",
        "role": "Gestión distribuida de cambios, integridad criptográfica y trazabilidad de código.",
        "why": "Permite a cientos de desarrolladores colaborar sobre el mismo código simultáneamente sin pisarse cambios ni perder historial.",
        "internal_mechanics": "Árboles de Merkle, hashes SHA-1/SHA-256 inmutables, base de datos de objetos (blob, tree, commit, tag) y punteros atómicos actualizados en `.git/refs`."
    },
    "contenerización-y-orquestación": {
        "title": "Contenerización y Orquestación",
        "semester": "Núcleo Profesional",
        "role": "Empaquetado inmutable de entornos y gestión declarativa de clústeres a escala.",
        "why": "Elimina el clásico 'en mi máquina sí funciona' y permite autoscaling horizontal, auto-healing y despliegues sin interrupción.",
        "internal_mechanics": "Aislamiento de namespaces de Linux (PID, NET, MNT), cuotas de recursos con cgroups, capas de sistema de archivos UnionFS (Overlay2) y bucle de reconciliación en Kubernetes."
    },
    "devops-ci-cd-e-iac": {
        "title": "DevOps, CI/CD e Infraestructura como Código (IaC)",
        "semester": "Núcleo Profesional",
        "role": "Automatización del ciclo de entrega de valor e infraestructura declarativa reproducible.",
        "why": "Desplegar manualmente por SSH es lento y propenso a errores humanos catastróficos. CI/CD e IaC convierten la infraestructura en código versionable y testeable.",
        "internal_mechanics": "Pipelines de runners efímeros, reconciliación de grafos dirigidos acíclicos (DAG) en Terraform, gestión de estado y secretos inyectados en runtime vía OIDC."
    },
    "cloud-aws": {
        "title": "Cloud Computing (Amazon Web Services)",
        "semester": "Núcleo Profesional",
        "role": "Infraestructura elástica global, almacenamiento distribuido y servicios gestionados.",
        "why": "Permite a empresas pasar de cero a escala global en minutos sin invertir millones en datacenters físicos propios.",
        "internal_mechanics": "Regiones compuestas por múltiples Availability Zones interconectadas por fibra oscura dedicada, orquestadas por hipervisores Nitro y almacenamiento EBS/S3 distribuido."
    },
    "caching-y-mensajería": {
        "title": "Caching y Mensajería Asíncrona",
        "semester": "Núcleo Profesional",
        "role": "Desacoplamiento temporal, absorción de picos de tráfico y optimización de latencia en lectura.",
        "why": "Las bases de datos disco son el cuello de botella común en alta concurrencia. El caché en memoria y las colas asíncronas salvan al sistema del colapso.",
        "internal_mechanics": "Almacenamiento en RAM con estructuras de datos en C (Redis) con políticas LRU/LFU, logs append-only distribuidos (Kafka) y colas AMQP con acuse de recibo (ACK)."
    },
    "seguridad": {
        "title": "Ciberseguridad y Seguridad de Aplicaciones (AppSec)",
        "semester": "Núcleo Profesional",
        "role": "Protección de activos digitales, criptografía, autenticación y análisis de vulnerabilidades.",
        "why": "Una brecha de seguridad puede costar millones en multas y destruir irreparablemente la confianza de los clientes.",
        "internal_mechanics": "Cifrado asimétrico (RSA/ECC) para intercambio de claves, simétrico (AES-GCM) para datos en tránsito y en reposo, firmas criptográficas y prevención de OWASP Top 10."
    },
    "testing": {
        "title": "Testing y Calidad de Software (QA)",
        "semester": "Núcleo Profesional",
        "role": "Verificación automatizada de comportamiento esperado y regresión continua.",
        "why": "Entregar código sin pruebas automatizadas significa que los usuarios finales serán los testers en producción.",
        "internal_mechanics": "Pirámide de testing (unitarias, integración, e2e), dobles de prueba (mocks, stubs, fakes), assertions deterministas y reportes de cobertura de código."
    },
    "observabilidad": {
        "title": "Observabilidad (Logs, Métricas, Trazas)",
        "semester": "Núcleo Profesional",
        "role": "Inferencia del estado interno de un sistema complejo a partir de sus salidas externas.",
        "why": "En sistemas distribuidos, cuando una petición falla no puedes poner un breakpoint: necesitas telemetría para correlacionar eventos en milisegundos.",
        "internal_mechanics": "Estándar OpenTelemetry (OTel), propagación de contexto en cabeceras HTTP (W3C TraceContext), series temporales en bases de datos TSDB (Prometheus) y agregación de logs en JSON."
    },
    "arquitectura-y-diseño": {
        "title": "Arquitectura de Software y Patrones de Diseño",
        "semester": "Núcleo Profesional",
        "role": "Estructuración estratégica de componentes, límites de dominio y comunicación inter-sistema.",
        "why": "Una mala arquitectura convierte cualquier adición de funcionalidad en una pesadilla que requiere reescribir medio sistema.",
        "internal_mechanics": "Clean Architecture, Puertos y Adaptadores (Hexagonal), Event-Driven Architecture (EDA) y patrones GoF (Creacionales, Estructurales, de Comportamiento)."
    },
    "apis-e-integraciones": {
        "title": "APIs y Protocolos de Integración",
        "semester": "Núcleo Profesional",
        "role": "Contratos de comunicación entre sistemas heterogéneos y clientes multiplataforma.",
        "why": "Permite que diferentes servicios desarrollados en distintos lenguajes y plataformas interactúen de forma estandarizada y segura.",
        "internal_mechanics": "REST sobre HTTP con hipermedios o JSON, RPC binario sobre HTTP/2 mediante Protobuf (gRPC), esquemas tipados con GraphQL y webhooks reactivos."
    },
    "ia-nueva-era-sección-ampliada": {
        "title": "Inteligencia Artificial y Sistemas Agénticos",
        "semester": "Frontera Tecnológica",
        "role": "Modelos de Lenguaje Grande (LLMs), RAG, protocolos agénticos y automatización cognitiva.",
        "why": "La mayor transformación en la industria del software: sistemas que no solo procesan reglas rígidas, sino que comprenden lenguaje natural, razonan y ejecutan herramientas.",
        "internal_mechanics": "Mecanismo de atención (Self-Attention) en arquitecturas Transformer, bases de datos vectoriales con búsqueda por similitud del coseno (HNSW), y protocolos abiertos como MCP."
    },
    "hosting-paas-y-plataformas": {
        "title": "Hosting, PaaS y Plataformas Serverless",
        "semester": "Núcleo Profesional",
        "role": "Plataformas de despliegue gestionado de código directo a producción.",
        "why": "Permite a los equipos centrarse 100% en el código de negocio delegando el aprovisionamiento de servidores, TLS y balanceo a la plataforma.",
        "internal_mechanics": "Buildpacks que detectan el lenguaje y compilan imágenes OCI, routers Anycast globales y despliegues atómicos sin caída mediante swaps de DNS."
    },
    "formatos-y-serialización": {
        "title": "Formatos de Datos y Serialización",
        "semester": "Núcleo Profesional",
        "role": "Codificación y decodificación eficiente de estructuras de datos en memoria a bytes para transporte o almacenamiento.",
        "why": "Elegir el formato incorrecto puede multiplicar por 10 el ancho de banda consumido y saturar la CPU en parsing innecesario.",
        "internal_mechanics": "Formatos de texto legibles por humanos (JSON, YAML, XML) versus formatos binarios compactos con esquema estricto (Protocol Buffers, Avro, MessagePack, Parquet)."
    },
    "frameworks-y-librerías": {
        "title": "Frameworks y Librerías de Producción",
        "semester": "Núcleo Profesional",
        "role": "Conjuntos preconstruidos de herramientas y abstracciones para acelerar el desarrollo.",
        "why": "Reinventar la rueda en enrutamiento HTTP, validación de formularios o seguridad básica es un desperdicio masivo de tiempo y una fuente de vulnerabilidades.",
        "internal_mechanics": "Inversión de Control (IoC), inyección de dependencias, middlewares en cascada y abstracciones ORM/ODM para interacción transparente con datos."
    },
    "productividad-conocimiento-y-colaboración": {
        "title": "Productividad, Gestión del Conocimiento y Documentación",
        "semester": "Núcleo Profesional",
        "role": "Gestión del capital intelectual, wikis técnicas y herramientas de eficiencia de ingeniería.",
        "why": "Si el conocimiento de un sistema solo reside en la cabeza de un ingeniero, la empresa sufre de un riesgo crítico (factor de autobús).",
        "internal_mechanics": "Grafos de conocimiento bidireccionales (Obsidian/Zettelkasten), documentación como código (Docs-as-Code con Markdown) y registros de decisiones arquitectónicas (ADRs)."
    },
    "arquitecturas-de-software-uml-c4-adr": {
        "title": "Modelado de Arquitecturas (UML, Modelo C4 y ADRs)",
        "semester": "Núcleo Profesional",
        "role": "Notación visual estandarizada y registro formal de decisiones arquitectónicas.",
        "why": "Permite comunicar la estructura y comportamiento de un sistema a diferentes audiencias (desde negocio hasta desarrolladores) sin ambigüedades.",
        "internal_mechanics": "Modelo C4 con zoom jerárquico progresivo (Contexto, Contenedores, Componentes, Código) y fichas inmutables ADR que capturan contexto, decisión y consecuencias."
    },
    "arquitectura": {
        "title": "Documentos Propios de Arquitectura",
        "semester": "Especialidad Interna",
        "role": "Patrones de arquitectura limpios aplicados directamente a proyectos reales.",
        "why": "Aterriza los conceptos teóricos de desacoplamiento en carpetas, entidades, casos de uso y puertos adaptadores.",
        "internal_mechanics": "Regla de dependencia concéntrica: las capas internas (dominio) nunca conocen ni dependen de las externas (frameworks, bases de datos, UI)."
    },
    "documentacion": {
        "title": "Documentación Formal de Proyectos",
        "semester": "Especialidad Interna",
        "role": "Plantillas maestras de especificación técnica, funcional, diseño y soporte.",
        "why": "Asegura la entrega integral de un proyecto con calidad industrial para auditorías, clientes y equipos de operaciones.",
        "internal_mechanics": "Estructuras formales de Documentos Funcionales (PRD), Arquitectura de Infraestructura (ADD), Sistemas de Diseño (Design System) y Planes de Soporte."
    }
}
