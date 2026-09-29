# Prompts — Axiom Meridian

Este documento consolida en un solo archivo los prompts usados durante el desarrollo de Axiom Meridian, previamente distribuidos en la carpeta `prompts/` (9 archivos numerados). Se listan como máximo 3 prompts por sección, priorizando los de creación inicial y los de corrección/adición de funcionalidades más relevantes. Cuando un mismo prompt generó contenido relevante para varias secciones, se reproduce una sola vez y se enlaza desde las demás para no duplicar texto.

## Índice

1. [Descripción general del producto](#1-descripción-general-del-producto)
2. [Arquitectura del sistema](#2-arquitectura-del-sistema)
3. [Modelo de datos](#3-modelo-de-datos)
4. [Especificación de la API](#4-especificación-de-la-api)
5. [Historias de usuario](#5-historias-de-usuario)
6. [Tickets de trabajo](#6-tickets-de-trabajo)
7. [Pull requests](#7-pull-requests)

---

## 1. Descripción general del producto

**Prompt 1:** *(creación inicial — fuente original: `01-documentation-baseline.md`)*

> **Prompt: baseline de documentación del proyecto (`docs/`)**
>
> **Contexto/Role:** Estás documentando desde cero Axiom Meridian, un servidor MCP (Model Context Protocol) que centraliza reglas y lecciones aprendidas institucionales y entrega solo la porción relevante a la tarea actual. Es el proyecto capstone de una Maestría en Inteligencia Artificial de Juan Rojas. Toda la documentación debe escribirse en inglés, para mantener consistencia con el tooling de IA usado en todo el proyecto (Claude Code, clientes MCP).
>
> **Objetivo/Tarea:** Crear la documentación base del proyecto en `docs/`, numerada del 01 al 06, que sirva como fuente de verdad narrativa antes de escribir una sola línea de código: charter, descripción de producto, arquitectura de sistema, modelo de datos, historias de usuario y tickets de trabajo. Actualizar `README.md` para indexarla.
>
> **Criterios de éxito explícitos** (se cumplen cuando):
> - `docs/01-project-charter.md` tiene fact sheet (nombre, tagline, pitch, autor, contexto académico, versión, licencia, lenguaje/framework principal, persistencia, interfaces, distribución), elevator pitch, objetivos, alcance y stakeholders.
> - `docs/02-product-description.md` cubre problema, solución, capacidades core, usuarios objetivo, por qué no alcanza con grep sobre Markdown, non-goals de v1 y posición en el ecosistema.
> - `docs/03-system-architecture.md` describe principios guía, vista de alto nivel, capas, flujo de lectura (`query_rules`), flujo de escritura (proposal → approval), modelo de seguridad, transporte, invariantes clave, stack tecnológico y un log de decisiones de arquitectura (ADRs).
> - `docs/04-data-model.md` incluye diagrama entidad-relación, referencia de tablas, ejemplo de jerarquía de scopes, formato de bloque atómico (con al menos un ejemplo de regla y uno de lección), estrategia de generación de IDs y freshness de lectura indexada.
> - `docs/05-user-stories.md` agrupa historias por Epic (A–H) en formato `As a / I want / so that`, con tool MCP asociado y prioridad MoSCoW.
> - `docs/06-work-tickets.md` separa tickets **Delivered** (con criterios de aceptación completos) de **Backlog** (candidatos a implementar), cada uno trazado a su historia de usuario y/o ADR cuando aplique.
> - Cada documento termina con una sección "Related Documents" que enlaza a los otros cinco.
> - `README.md` tiene una tabla que enlaza los 6 documentos con una descripción de una línea cada uno.
>
> **Restricciones/Antipatterns:**
> - No duplicar los criterios de aceptación formales en `docs/05` — esos ya están destinados a vivir como specs en OpenSpec; en `docs/05` basta el formato narrativo `As a/I want/so that`.
> - No inventar decisiones de stack irreversibles (framework MCP, motor de persistencia) sin dejarlas explícitas como decisión, para que puedan auditarse después.
>
> **Recursos/Contexto:** No hay código existente que leer (repo vacío salvo `README.md`); basarse en la visión de producto que dé el autor del proyecto. `README.md` inicial del repo, para mantener tono y alcance.
>
> **Formato de salida:** Seis archivos Markdown en `docs/`, nombrados `01-project-charter.md` … `06-work-tickets.md`. `README.md` actualizado con una sección "Documentation" en formato tabla. Todo en inglés.
>
> **Clarificación:** Si hay ambigüedad sobre el stack tecnológico (por ejemplo: framework MCP a usar, motor de vector store, clientes a soportar en el instalador) o sobre qué queda en v1 vs. backlog, preguntar antes de fijarlo en `03-system-architecture.md` o `06-work-tickets.md` — son decisiones caras de revertir una vez que otros documentos (y luego OpenSpec) las referencian.

Este mismo prompt generó también `docs/03-system-architecture.md` (ver [Sección 2](#2-arquitectura-del-sistema)), `docs/04-data-model.md` (ver [Sección 3](#3-modelo-de-datos)) y `docs/05-user-stories.md` / `docs/06-work-tickets.md` (ver [Sección 5](#5-historias-de-usuario) y [Sección 6](#6-tickets-de-trabajo)).

---

## 2. Arquitectura del Sistema

### **2.1. Diagrama de arquitectura:**

Los diagramas (Mermaid) de vista de alto nivel y de los flujos de lectura/escritura en `docs/03-system-architecture.md` se generaron con el mismo prompt de creación de la documentación base. Ver **Prompt 1** en la [Sección 1](#1-descripción-general-del-producto).

### **2.2. Descripción de componentes principales:**

Las capas, invariantes clave y stack tecnológico también provienen del prompt de baseline documental. Ver **Prompt 1** en la [Sección 1](#1-descripción-general-del-producto).

### **2.3. Descripción de alto nivel del proyecto y estructura de ficheros**

La vista de alto nivel y el log de decisiones de arquitectura (ADRs) provienen del mismo prompt de baseline. Ver **Prompt 1** en la [Sección 1](#1-descripción-general-del-producto).

### **2.4. Infraestructura y despliegue**

**Prompt 1:** *(adición de funcionalidad — fuente original: `03-opsx-ff-add-windows-installer.md`)*

> **Prompt: change `add-windows-installer` vía `/opsx:ff`**
>
> **Contexto/Role:** El proyecto Axiom Meridian, tendrá un instalador `scripts/install.sh` para Linux/macOS con auto-detección de clientes MCP (Claude Code, VSCode, OpenCode, Kimi CLI) e instalación en una línea. Windows no tiene equivalente (TICKET-012, backlog). OpenSpec ya tiene su baseline en `openspec/specs/`.
>
> **Objetivo/Tarea:** Usando `/opsx:ff add-windows-installer`, generar el change completo (proposal, delta spec, design y tasks) que agregue un instalador de Windows equivalente a `install.sh`, sin implementarlo todavía.
>
> **Criterios de éxito explícitos** — `openspec/changes/add-windows-installer/` debe tener:
> - `proposal.md` con `## Why` (fricción actual en Windows), `## What Changes` (nuevo `scripts/install.ps1` con paridad de comportamiento con `install.sh`), `## Capabilities` → `New Capabilities: installation`, y `## Impact` (archivo nuevo + actualización de README/docs de instalación).
> - `specs/installation/spec.md` como delta spec con al menos un `Requirement` en formato BDD (`Scenario:` con GIVEN/WHEN/THEN) cubriendo el instalador de Windows.
> - `design.md` con `Context`, `Goals/Non-Goals` (explícitamente: no reescribir `install.sh`, no empaquetar un `.exe`/MSI firmado), `Decisions` (script PowerShell nativo, no runtime cross-platform nuevo) y `Risks/Trade-offs` (mantener dos scripts sincronizados).
> - `tasks.md` con checklist sin marcar (`[ ]`), agrupado en secciones (instalador, distribución, verificación), incluyendo al menos una tarea de verificación manual en un entorno Windows limpio.
> - `.openspec.yaml` presente con `schema: spec-driven`.
>
> **Restricciones/Antipatterns:**
> - No ejecutar `/opsx:apply` en este prompt — solo se generan artefactos, no se escribe `scripts/install.ps1` todavía.
> - No expandir el alcance a otros instaladores (Linux ARM, Docker, etc.) — el Impact se limita a Windows.
> - No marcar ninguna tarea de `tasks.md` como completada.
>
> **Recursos/Contexto:** `docs/06-work-tickets.md` — TICKET-012. `openspec/specs/` — no existe una capability `installation` en la baseline (el instalador Unix nunca se documentó como spec), así que esta es una **New Capability**, no un delta sobre algo existente.
>
> **Formato de salida:** Carpeta `openspec/changes/add-windows-installer/` con `proposal.md`, `specs/installation/spec.md`, `design.md`, `tasks.md` y `.openspec.yaml`.
>
> **Clarificación:** Si al escribir `design.md` surge la duda de si vale la pena empaquetar un instalador firmado en vez de un script PowerShell plano, preguntar antes de fijarlo como Non-Goal — es una decisión de superficie de mantenimiento a largo plazo.
>
> **Comandos OpenSpec ejecutados** (skill `openspec-ff-change`, `/opsx:ff`):
> ```bash
> openspec new change "add-windows-installer"
> openspec status --change "add-windows-installer" --json
> openspec instructions proposal --change "add-windows-installer" --json
> # → escribir proposal.md
> openspec instructions specs --change "add-windows-installer" --json
> # → escribir specs/installation/spec.md
> openspec instructions design --change "add-windows-installer" --json
> # → escribir design.md
> openspec instructions tasks --change "add-windows-installer" --json
> # → escribir tasks.md
> openspec status --change "add-windows-installer"
> ```

### **2.5. Seguridad**

**Prompt 1:** *(adición de funcionalidad — fuente original: `06-opsx-ff-harden-networked-deployment.md`)*

> **Prompt: change `harden-networked-deployment` vía `/opsx:ff`**
>
> **Contexto/Role:** El transporte HTTP/SSE de Axiom Meridian está restringido por diseño a `127.0.0.1` (parte de la capability baseline `security-access-control`). Hay equipos que quieren un despliegue compartido en red, pero quitar la restricción de localhost sin más crearía un vector de takeover remoto de la base de conocimiento (TICKET-015, backlog).
>
> **Objetivo/Tarea:** Usando `/opsx:ff harden-networked-deployment`, generar el change completo que documente el threat model de un despliegue en red y proponga un modo opt-in endurecido (TLS, auth multi-token/por cliente, rate limiting), sin debilitar el comportamiento localhost-only.
>
> **Criterios de éxito explícitos** — `openspec/changes/harden-networked-deployment/` debe tener:
> - `proposal.md` con `## Why` (sin camino soportado hoy para despliegue en red), `## What Changes` (threat model documentado + flag de configuración opt-in con TLS/auth/rate limiting, estrictamente aditivo), `## Capabilities` → `Modified Capabilities: security-access-control`, `## Impact` (código de configuración/arranque del transporte + nueva documentación de threat model).
> - `specs/security-access-control/spec.md` como **delta** sobre la baseline existente, con `ADDED Requirements` para el modo en red opt-in y explícitamente sin `MODIFIED`/`REMOVED` sobre el comportamiento localhost-only por defecto.
> - `design.md` con `Goals/Non-Goals` (goal: modo opt-in endurecido; non-goal: cambiar el default), `Decisions` sobre TLS/auth/rate limiting, y `Risks/Trade-offs` explícitos sobre superficie de ataque ampliada.
> - `tasks.md` con checklist sin marcar: threat model, flag de configuración, TLS, auth multi-token, rate limiting, verificación de que el default no cambió.
>
> **Restricciones/Antipatterns:**
> - No debilitar ni quitar el comportamiento localhost-only / single-token por defecto bajo ninguna circunstancia — el proposal es explícito: "strictly additive".
> - No implementar código todavía — solo generar los artefactos del change.
> - No omitir el threat model en `design.md`; es la pieza central que justifica por qué esto no es simplemente "quitar el bind a 127.0.0.1".
>
> **Recursos/Contexto:** `docs/06-work-tickets.md` — TICKET-015 (Related story: US-E3). `docs/03-system-architecture.md` — sección de modelo de seguridad y transporte. `openspec/specs/security-access-control/spec.md` — spec baseline sobre la que este change calcula su delta.
>
> **Formato de salida:** Carpeta `openspec/changes/harden-networked-deployment/` con `proposal.md`, `specs/security-access-control/spec.md` (delta), `design.md`, `tasks.md` y `.openspec.yaml`.
>
> **Clarificación:** Si no está claro qué mecanismo de auth multi-token/per-client se prefiere (tokens estáticos por cliente vs. algo tipo OAuth), preguntar antes de fijarlo como decisión en `design.md` — es una decisión de seguridad, no de conveniencia de implementación.
>
> **Comandos OpenSpec ejecutados** (skill `openspec-ff-change`, `/opsx:ff`):
> ```bash
> openspec new change "harden-networked-deployment"
> openspec status --change "harden-networked-deployment" --json
> openspec instructions proposal --change "harden-networked-deployment" --json
> openspec instructions specs --change "harden-networked-deployment" --json
> openspec instructions design --change "harden-networked-deployment" --json
> openspec instructions tasks --change "harden-networked-deployment" --json
> openspec status --change "harden-networked-deployment"
> ```

### **2.6. Tests**

No existe un prompt dedicado exclusivamente a tests: la verificación se incorpora como checklist dentro de `tasks.md` de cada change generado vía `/opsx:ff` (ver Prompts de las secciones [2.4](#24-infraestructura-y-despliegue), [2.5](#25-seguridad), [4](#4-especificación-de-la-api) y [6](#6-tickets-de-trabajo)), y como tarea de verificación de implementación vía la skill `openspec-verify-change`/`/opsx:verify`.

---

### 3. Modelo de Datos

**Prompt 1:** *(creación inicial)* — Ver **Prompt 1** en la [Sección 1](#1-descripción-general-del-producto): el mismo prompt de baseline documental generó `docs/04-data-model.md` (diagrama entidad-relación, referencia de tablas, jerarquía de scopes, formato de bloque atómico, generación de IDs y freshness de lectura indexada).

**Prompt 2:** *(adición de funcionalidad — fuente original: `07-opsx-ff-link-source-ref-to-engram.md`)*

> **Prompt: change `link-source-ref-to-engram` vía `/opsx:ff`**
>
> **Contexto/Role:** Donde Engram (memoria episódica de sesión) coexiste con Axiom Meridian, el `source_ref` de una regla o lección no tiene hoy forma de resolver a la observación de Engram que la originó, perdiendo trazabilidad cruzada entre herramientas (TICKET-016, backlog). Meridian debe seguir funcionando idéntico si Engram no está presente.
>
> **Objetivo/Tarea:** Usando `/opsx:ff link-source-ref-to-engram`, generar el change completo que permita que `source_ref` resuelva opcionalmente a un `observation_id` de Engram, y que `get_rule_context` pueda mostrar esa observación vinculada.
>
> **Criterios de éxito explícitos** — `openspec/changes/link-source-ref-to-engram/` debe tener:
> - `proposal.md` con `## Why` (trazabilidad cruzada perdida hoy), `## What Changes` (`source_ref` resuelve opcionalmente a `observation_id`; `get_rule_context` puede surfacear la observación vinculada; sin dependencia dura de Engram), `## Capabilities` → `Modified Capabilities: scoped-knowledge-consumption`, `## Impact` (implementación de `get_rule_context` + nuevo helper de resolución de `source_ref`, dependencia blanda de Engram, no-op cuando está ausente).
> - `specs/scoped-knowledge-consumption/spec.md` como **delta** sobre la baseline existente, con `MODIFIED Requirements` sobre `get_rule_context` y al menos dos `Scenario`: uno con Engram presente (observación vinculada visible) y uno con Engram ausente (comportamiento idéntico al actual).
> - `design.md` con `Goals/Non-Goals` (goal: trazabilidad opcional; non-goal: introducir una dependencia dura de Engram), `Decisions` sobre el helper de resolución, y `Risks/Trade-offs` (acoplamiento futuro entre los dos proyectos).
> - `tasks.md` con checklist sin marcar cubriendo el helper de resolución, el cambio en `get_rule_context`, y pruebas con y sin Engram presente.
>
> **Restricciones/Antipatterns:**
> - No introducir una dependencia dura (import obligatorio, requerimiento de instalación) de Engram — debe seguir siendo soft/no-op cuando está ausente.
> - No cambiar el comportamiento de `get_rule_context` cuando no hay Engram; el requirement `MODIFIED` debe dejar ese caso explícitamente sin cambios.
> - No expandir el alcance a otros tools además de `get_rule_context`.
>
> **Recursos/Contexto:** `docs/06-work-tickets.md` — TICKET-016. `openspec/specs/scoped-knowledge-consumption/spec.md` — spec baseline sobre la que este change calcula su delta (incluye `get_rule_context` y `get_rule_timeline`).
>
> **Formato de salida:** Carpeta `openspec/changes/link-source-ref-to-engram/` con `proposal.md`, `specs/scoped-knowledge-consumption/spec.md` (delta), `design.md`, `tasks.md` y `.openspec.yaml`.
>
> **Clarificación:** Si no está definido el contrato exacto de Engram (formato de `observation_id`, cómo se descubre si Engram está instalado), preguntar antes de fijar el diseño del helper de resolución — es una integración con un proyecto externo, no un detalle interno.
>
> **Comandos OpenSpec ejecutados** (skill `openspec-ff-change`, `/opsx:ff`):
> ```bash
> openspec new change "link-source-ref-to-engram"
> openspec status --change "link-source-ref-to-engram" --json
> openspec instructions proposal --change "link-source-ref-to-engram" --json
> openspec instructions specs --change "link-source-ref-to-engram" --json
> openspec instructions design --change "link-source-ref-to-engram" --json
> openspec instructions tasks --change "link-source-ref-to-engram" --json
> openspec status --change "link-source-ref-to-engram"
> ```

---

### 4. Especificación de la API

En Axiom Meridian, la "API" son los tools MCP expuestos (`query_rules`, `query_lessons`, `get_rule_context`, etc.), formalizados como specs OpenSpec en formato `Requirement`/`Scenario` (BDD).

**Prompt 1:** *(creación inicial — fuente original: `02-openspec-baseline-specs.md`)*

> **Prompt: specs baseline de capacidades ya entregadas (`openspec/specs/`)**
>
> **Contexto/Role:** Ya existen `docs/05-user-stories.md` (Epics A–H) y `docs/06-work-tickets.md`, con once tickets ya en estado **Delivered** (TICKET-001 a TICKET-011, trazados a los Epics A–G). La herramienta OpenSpec ya está inicializada, pero `openspec/specs/` sigue vacío.
>
> **Objetivo/Tarea:** Materializar en `openspec/specs/` una spec por capability ya construida, que describa el comportamiento **actual** del sistema (no un delta de un cambio futuro), para que sirva de línea base contra la que los `changes/` calculen sus deltas más adelante.
>
> **Criterios de éxito explícitos:**
> - Existen exactamente 7 capabilities bajo `openspec/specs/`: `ecosystem-integration`, `knowledge-lifecycle-governance`, `pr-and-planning-audits`, `scoped-knowledge-consumption`, `security-access-control`, `semantic-search`, `transcript-extraction` — cada una con su `spec.md`.
> - Cada `spec.md` usa el formato `Requirement` / `Scenario` (BDD, GIVEN/WHEN/THEN) — el mismo formato que usarán los delta specs de los changes futuros.
> - Cada requirement traza a los tickets Delivered (001–011) y a las historias de usuario de los Epics A–G correspondientes.
> - El Epic H (dashboard) **no** tiene spec baseline — todavía es backlog, no algo entregado.
> - `openspec list --specs` (o `openspec validate`) no reporta errores de formato sobre estos 7 archivos.
>
> **Restricciones/Antipatterns:** No crear una capability nueva por cada ticket 1:1 si varios tickets delivered describen la misma capability (agrupar por Epic, no por ticket).
>
> **Recursos/Contexto:** `docs/05-user-stories.md` — Epics A–G y sus historias. `docs/06-work-tickets.md` — sección Delivered, TICKET-001 a TICKET-011. `docs/03-system-architecture.md` — modelo de seguridad y transporte (insumo directo para `security-access-control`).
>
> **Formato de salida:** Siete archivos `openspec/specs/<capability>/spec.md`, sin `proposal.md`, `design.md` ni `tasks.md` acompañándolos (esos son artefactos de `changes/`, no de la baseline).
>
> **Clarificación:** Si un ticket Delivered no mapea limpiamente a ninguna epic/capability existente, preguntar cómo nombrar la capability antes de crear una carpeta nueva bajo `openspec/specs/`.
>
> **Comandos OpenSpec ejecutados:** ninguno del flujo `opsx` (`openspec new change`, `openspec instructions`, etc.): estos archivos se escriben **directamente**, porque describen capacidades ya entregadas y no pasan por proposal → design → tasks. Como mucho, se usa:
> ```bash
> openspec list --specs
> openspec validate
> ```
> para confirmar que el formato de los 7 `spec.md` es válido una vez escritos.

**Prompt 2:** *(corrección/evolución de funcionalidad existente — fuente original: `04-opsx-ff-upgrade-semantic-search-v2.md`)*

> **Prompt: change `upgrade-semantic-search-v2` vía `/opsx:ff`**
>
> **Contexto/Role:** Axiom Meridian ya tiene una capability `semantic-search` en la baseline (`openspec/specs/semantic-search/spec.md`), basada en el modelo de embeddings `bge-small-en-v1.5` y un vector store local. TICKET-013 (backlog) plantea que, al crecer el volumen de reglas/lecciones más allá de ~1000 entradas, o si se necesita mejor retrieval multilingüe, ese modelo puede no alcanzar.
>
> **Objetivo/Tarea:** Usando `/opsx:ff upgrade-semantic-search-v2`, generar el change completo que evalúe migrar a `BAAI/bge-m3` y/o a un vector store alternativo (LanceDB, Qdrant local), sin romper la firma de `query_rules`/`query_lessons`.
>
> **Criterios de éxito explícitos** — `openspec/changes/upgrade-semantic-search-v2/` debe tener:
> - `proposal.md` con `## Why` (umbral de ~1000 entradas / necesidad multilingüe), `## What Changes` (evaluar `bge-m3` y vector stores alternativos, sin cambios a firmas de tools ni al esquema SQLite), `## Capabilities` → `Modified Capabilities: semantic-search`, `## Impact` (internals de `generate_embeddings`, adapter de vector store, nuevo artefacto de benchmark).
> - `specs/semantic-search/spec.md` como **delta** sobre la spec baseline existente, usando secciones `MODIFIED Requirements` (no `ADDED`, porque la capability ya existe) con al menos un `Scenario` que cubra que el modelo/vector store son intercambiables sin cambiar el contrato de `query_rules`/`query_lessons`.
> - `design.md` con `Goals/Non-Goals` (goal: swappable embedding backend; non-goal: cambiar firmas de tools o el esquema), `Decisions` y una sección de `Risks/Trade-offs` que mencione el costo de mantener un benchmark comparativo.
> - `tasks.md` con checklist agrupado en evaluación de modelo, evaluación de vector store, benchmark y verificación — todas sin marcar.
>
> **Restricciones/Antipatterns:**
> - No tocar el esquema de SQLite ni las firmas de `query_rules`/`query_lessons` — eso está explícitamente fuera de alcance según el ticket.
> - No fijar `bge-m3` como decisión definitiva sin dejar constancia de que es una **evaluación** (el proposal dice "Evaluate migrating…", no "Migrate").
> - No omitir el requisito de comparación cuantitativa (benchmark) en `design.md` o `tasks.md` — sin eso no hay forma de justificar el cambio de modelo.
>
> **Recursos/Contexto:** `docs/06-work-tickets.md` — TICKET-013 (Related story: US-F1). `openspec/specs/semantic-search/spec.md` — spec baseline sobre la que este change calcula su delta.
>
> **Formato de salida:** Carpeta `openspec/changes/upgrade-semantic-search-v2/` con `proposal.md`, `specs/semantic-search/spec.md` (delta), `design.md`, `tasks.md` y `.openspec.yaml`.
>
> **Clarificación:** Si no está claro qué vector stores alternativos son candidatos serios (LanceDB vs. Qdrant local vs. otro), preguntar antes de fijarlos en `design.md` — son decisiones de dependencia externa, no de implementación interna.
>
> **Comandos OpenSpec ejecutados** (skill `openspec-ff-change`, `/opsx:ff`):
> ```bash
> openspec new change "upgrade-semantic-search-v2"
> openspec status --change "upgrade-semantic-search-v2" --json
> openspec instructions proposal --change "upgrade-semantic-search-v2" --json
> openspec instructions specs --change "upgrade-semantic-search-v2" --json
> openspec instructions design --change "upgrade-semantic-search-v2" --json
> openspec instructions tasks --change "upgrade-semantic-search-v2" --json
> openspec status --change "upgrade-semantic-search-v2"
> ```

**Prompt 3:** *(adición de funcionalidad — fuente original: `05-opsx-ff-add-redundancy-detection.md`)*

> **Prompt: change `add-redundancy-detection` vía `/opsx:ff`**
>
> **Contexto/Role:** A medida que crece el set de reglas de Axiom Meridian a través de scopes, aparecen reglas casi-duplicadas o solapadas (la misma restricción reescrita ligeramente distinto en dos proyectos). Hoy nada las detecta para que un curador las revise (TICKET-014, backlog). Ya existen embeddings gracias a la capability `semantic-search`.
>
> **Objetivo/Tarea:** Usando `/opsx:ff add-redundancy-detection`, generar el change completo para una nueva capability de detección de redundancia: un reporte de solo lectura para curadores, basado en clustering por similitud de embeddings.
>
> **Criterios de éxito explícitos** — `openspec/changes/add-redundancy-detection/` debe tener:
> - `proposal.md` con `## Why` (acumulación de reglas casi-duplicadas entre scopes), `## What Changes` (clustering por similitud + reporte curator-facing; sin merge ni escritura automática), `## Capabilities` → `New Capabilities: redundancy-detection`, `## Impact` (nuevo tool de solo lectura sobre embeddings existentes, sin escrituras de esquema ni cambios a firmas de tools existentes).
> - `specs/redundancy-detection/spec.md` con `ADDED Requirements` (capability nueva) y al menos un `Scenario` que cubra: pares de reglas por encima de un umbral de similitud aparecen en el reporte, y que el reporte nunca escribe ni fusiona reglas automáticamente.
> - `design.md` con `Goals/Non-Goals` (goal: reporte informativo; non-goal: merge automático), `Decisions` sobre el umbral de similitud y el algoritmo de clustering, y `Risks/Trade-offs` (falsos positivos/negativos del umbral).
> - `tasks.md` con checklist sin marcar, cubriendo el tool de solo lectura, el clustering, el formato del reporte y su verificación.
>
> **Restricciones/Antipatterns:**
> - No introducir ninguna escritura a `rules`/`lessons` ni un flujo de auto-merge — el proposal es explícito en que el reporte es solo informativo.
> - No duplicar la generación de embeddings — este change se apoya en los embeddings que ya produce `semantic-search`, no genera los suyos.
> - No cambiar la firma de ningún tool existente.
>
> **Recursos/Contexto:** `docs/06-work-tickets.md` — TICKET-014. `openspec/specs/semantic-search/spec.md` — de dónde vienen los embeddings que este change reutiliza.
>
> **Formato de salida:** Carpeta `openspec/changes/add-redundancy-detection/` con `proposal.md`, `specs/redundancy-detection/spec.md`, `design.md`, `tasks.md` y `.openspec.yaml`.
>
> **Clarificación:** Si no está definido qué umbral de similitud cuenta como "candidato a duplicado", preguntar antes de fijar un número en `design.md` — es un parámetro que afecta directamente cuánto ruido ve el curador.
>
> **Comandos OpenSpec ejecutados** (skill `openspec-ff-change`, `/opsx:ff`):
> ```bash
> openspec new change "add-redundancy-detection"
> openspec status --change "add-redundancy-detection" --json
> openspec instructions proposal --change "add-redundancy-detection" --json
> openspec instructions specs --change "add-redundancy-detection" --json
> openspec instructions design --change "add-redundancy-detection" --json
> openspec instructions tasks --change "add-redundancy-detection" --json
> openspec status --change "add-redundancy-detection"
> ```

---

### 5. Historias de Usuario

**Prompt 1:** *(creación inicial)* — Ver **Prompt 1** en la [Sección 1](#1-descripción-general-del-producto): el mismo prompt de baseline documental generó `docs/05-user-stories.md` (Epics A–H, formato `As a/I want/so that`, tool MCP asociado y prioridad MoSCoW).

**Prompt 2:** *(corrección — fuente original: `09-fix-cross-link-docs-with-openspec.md`)*

> **Prompt: reconciliar `docs/` con el contenido ya creado en `openspec/`**
>
> **Contexto/Role:** `docs/05-user-stories.md` y `docs/06-work-tickets.md` se escribieron **antes** de que existiera contenido en `openspec/` y listan criterios de aceptación completos tanto para historias Delivered como Backlog. Ahora ya existen: 7 specs baseline en `openspec/specs/` y 6 changes en `openspec/changes/`. Los criterios de aceptación quedaron duplicados en dos lugares que pueden divergir.
>
> **Objetivo/Tarea:** Eliminar la duplicación de criterios de aceptación entre `docs/` y `openspec/`, dejando `openspec/` como la única fuente de verdad *formal y testeable*, y `docs/05`/`docs/06` como la fuente *narrativa* que enlaza hacia ella.
>
> **Criterios de éxito explícitos:**
> - `docs/05-user-stories.md`: cada historia de las Epics A–G ya no repite sus "Acceptance criteria" en formato Given/When/Then; en su lugar, cada Epic tiene una línea "Formal spec:" que enlaza a `openspec/specs/<capability>/spec.md` (o, para el Epic F, también al change en progreso `openspec/changes/upgrade-semantic-search-v2/`). El Epic H enlaza al change `add-observability-dashboard` con una nota de que todavía no es parte de la baseline.
> - `docs/06-work-tickets.md`: los tickets **Delivered** (001–011) conservan sus criterios de aceptación completos (no había spec baseline "delta" que los reemplace, y son historia, no trabajo formal en curso). Los tickets **Backlog** (012–017) reemplazan su bullet "Acceptance criteria" por un bullet "OpenSpec change:" que enlaza a `openspec/changes/<name>/`. Se agrega una nota introductoria en la sección `## Backlog` explicando que cada ticket ahí tiene un change correspondiente que sostiene el detalle formal.
> - `README.md`: la fila de la tabla de `05 · User Stories` deja de decir "with acceptance criteria" y pasa a aclarar que el detalle formal vive en `openspec/`.
> - Ambos documentos agregan `[OpenSpec specs and changes](../openspec/)` a su sección "Related Documents".
> - Ningún contenido técnico nuevo se inventa en este pase — es puramente reconciliación/enlace, no una nueva fuente de verdad.
>
> **Restricciones/Antipatterns:**
> - No borrar los criterios de aceptación de los tickets **Delivered** — esos no tienen contraparte formal en `openspec/` (no son un change), así que siguen siendo la única fuente para ellos.
> - No reescribir el contenido narrativo (`As a/I want/so that`) de las historias de usuario — el pase es solo sobre los criterios de aceptación duplicados, no sobre el resto del archivo.
> - No dejar un documento (`docs/` u `openspec/`) como la única fuente de verdad de forma inconsistente entre epics — el criterio (delivered → docs/06; backlog → openspec/changes) debe aplicarse parejo a los 17 tickets.
>
> **Recursos/Contexto:** `docs/05-user-stories.md` y `docs/06-work-tickets.md` en su versión previa a este pase. Los 7 `openspec/specs/*/spec.md` y los 6 `openspec/changes/*/proposal.md` ya creados, para saber a qué enlazar exactamente.
>
> **Formato de salida:** Edición in-place de `README.md`, `docs/05-user-stories.md` y `docs/06-work-tickets.md`. Sugerencia de mensaje de commit: algo corto que dé cuenta de que es una limpieza de duplicados, no una feature nueva (p. ej. "Removing duplicates").
>
> **Clarificación:** Si algún Epic no tiene todavía ni spec baseline ni change (no debería pasar tras los prompts anteriores, pero conviene verificarlo), preguntar cómo enlazarlo en vez de dejar el bullet "Formal spec:" apuntando a una ruta que no existe.

---

### 6. Tickets de Trabajo

**Prompt 1:** *(creación inicial)* — Ver **Prompt 1** en la [Sección 1](#1-descripción-general-del-producto): el mismo prompt de baseline documental generó `docs/06-work-tickets.md` (tickets Delivered vs. Backlog, trazados a historias de usuario y ADRs).

**Prompt 2:** *(corrección)* — Ver **Prompt 2** en la [Sección 5](#5-historias-de-usuario): reconciliación de `docs/06-work-tickets.md` con `openspec/changes/` (tickets Backlog reemplazan sus criterios de aceptación por enlaces a su change correspondiente).

**Prompt 3:** *(adición de funcionalidad — fuente original: `08-opsx-ff-add-observability-dashboard.md`)*

> **Prompt: change `add-observability-dashboard` vía `/opsx:ff`**
>
> **Contexto/Role:** Curadores y admins de Axiom Meridian hoy tienen que correr snippets de Python ad hoc o leer Markdown/SQLite crudo para entender el estado del sistema (salud del servidor, scopes indexados, conteos de reglas/lecciones, propuestas pendientes). Es TICKET-017 / US-H1, explícitamente fuera del alcance core del capstone (tools MCP, resolución de scopes, escrituras gobernadas, RAG) y evaluado solo si sobra tiempo después del backlog principal.
>
> **Objetivo/Tarea:** Usando `/opsx:ff add-observability-dashboard`, generar el change completo para un dashboard web de solo lectura, como proceso local separado, que incluya un proyector de embeddings como complemento visual a `redundancy-detection`.
>
> **Criterios de éxito explícitos** — `openspec/changes/add-observability-dashboard/` debe tener:
> - `proposal.md` con `## Why` (fricción de inspección manual hoy, explícitamente fuera del scope core y evaluado solo si sobra tiempo), `## What Changes` (dashboard read-only como proceso separado que importa `knowledge_consumption` como librería, sin hablar el protocolo MCP y sin escrituras; proyector de embeddings 2D/3D coloreado por scope/categoría/severidad), `## Capabilities` → `New Capabilities: observability-dashboard`, `## Impact` (nuevo proceso/paquete, sin cambios a `meridian.db` ni a ningún `.md`, sin generar embeddings nuevos — el proyector solo lee vectores ya existentes en ChromaDB).
> - `specs/observability-dashboard/spec.md` con `ADDED Requirements` y al menos un `Scenario` que cubra: el dashboard nunca invoca un tool de nivel `write`, y que corre bindeado a `127.0.0.1` por defecto.
> - `design.md` con `Goals/Non-Goals` (goal: vista read-only + proyector; non-goal: que hable MCP o que escriba), `Decisions` (FastAPI + frontend mínimo como capa separada) y `Risks/Trade-offs` (mantener un segundo stack fuera del scope core).
> - `tasks.md` con checklist sin marcar cubriendo backend read-only, vista de jerarquía de scopes, vista de propuestas pendientes, proyector de embeddings y verificación de que no hay escrituras.
>
> **Restricciones/Antipatterns:**
> - No hacer que el dashboard hable el protocolo MCP ni que llame ningún tool de nivel `write` (`approve_proposal`, `index_*`, `promote_rule`, `generate_embeddings`, …).
> - No generar embeddings nuevos desde el dashboard — el proyector solo lee los que ya existen en ChromaDB.
> - No perder de vista que esta capability es explícitamente opcional/nice-to-have — el `proposal.md` debe dejarlo constar, no presentarlo como core.
>
> **Recursos/Contexto:** `docs/06-work-tickets.md` — TICKET-017 (Related story: US-H1, epic opcional). `docs/03-system-architecture.md` — sección de transporte, para mantener consistencia de bind a `127.0.0.1`. `openspec/changes/add-redundancy-detection/` — de donde este dashboard toma el concepto de proyector como complemento visual al reporte numérico.
>
> **Formato de salida:** Carpeta `openspec/changes/add-observability-dashboard/` con `proposal.md`, `specs/observability-dashboard/spec.md`, `design.md`, `tasks.md` y `.openspec.yaml`.
>
> **Clarificación:** Si no está definido qué stack de frontend usar (server-rendered templates vs. HTMX vs. algo más), preguntar antes de fijarlo en `design.md` — es una decisión de dependencia nueva para un componente explícitamente opcional.
>
> **Comandos OpenSpec ejecutados** (skill `openspec-ff-change`, `/opsx:ff`):
> ```bash
> openspec new change "add-observability-dashboard"
> openspec status --change "add-observability-dashboard" --json
> openspec instructions proposal --change "add-observability-dashboard" --json
> openspec instructions specs --change "add-observability-dashboard" --json
> openspec instructions design --change "add-observability-dashboard" --json
> openspec instructions tasks --change "add-observability-dashboard" --json
> openspec status --change "add-observability-dashboard"
> ```

---

### 7. Pull Requests

No hay un prompt dedicado a la redacción de pull requests. La única PR mergeada hasta ahora (#1, "Removing duplicates") es el resultado directo del **Prompt 2** de la [Sección 5](#5-historias-de-usuario) (`09-fix-cross-link-docs-with-openspec.md`), cuyo propio "Formato de salida" sugirió el mensaje de commit/PR usado.
