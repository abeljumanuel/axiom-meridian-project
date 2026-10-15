# Plan — Habilitar MERIDIAN_MODE=shared (base de conocimiento en red)

**Fecha:** 2026-10-01 · **Estado:** Borrador, pendiente de retomar · **Base:** `add-actor-identity-tracking` (fundación de `actor_id`/`resolve_actor()`/`get_mode()`)

## Épica

Permitir que Axiom Meridian pase de "una instancia MCP local, un solo usuario" a "una base de conocimiento compartida en red, con proponentes y un grupo de validadores" — sin construir nada de esto como un big-bang. Hoy el servidor ya expone un modo `shared` reservado (`MERIDIAN_MODE=shared` existe como valor válido en `get_mode()`, pero `resolve_actor()` lanza `NotImplementedError` ahí) — esta épica es terminar esa implementación.

## Restricción central (no negociable)

**El modo local debe seguir funcionando exactamente igual durante todo el proceso.** Cada misión de esta épica se implementa y se mergea de forma que:
- `MERIDIAN_MODE` sin setear (o `"local"`) nunca cambia de comportamiento, en ningún punto intermedio.
- El modo `shared` solo se vuelve *alcanzable* al final de la implementación completa — no hay un estado intermedio donde el servidor quede parcialmente autenticado o con `check_access` a medio migrar. Hasta que todas las misiones estén listas, `MERIDIAN_MODE=shared` puede seguir fallando explícitamente (como hoy), nunca fallar silenciosamente o a medias.

Esto es consistente con cómo se construyó la fundación (`add-actor-identity-tracking`): cada pieza nueva es aditiva y verificada contra "cero regresión en local" antes de pasar a la siguiente.

## Qué ya existe (hecho, mergeado/en PR)

- `actor_id` (nullable) en `pending_proposals`, `rule_history`, `lesson_history`, `access_log` (migración 006).
- `utils/security.py::resolve_actor()`/`get_mode()`: en local, resuelve al usuario del SO sin credenciales; en `shared`, lanza `NotImplementedError` explícito (placeholder intencional, no un bug).
- `check_access` ya demostrado (con tests) como completamente desacoplado de `MERIDIAN_MODE` — la autorización no depende de la atribución.

## Hallazgo clave de la investigación (Context7 / FastMCP 3.2.4)

El servidor ya usa FastMCP 3.2.4 (pineado en `pyproject.toml`), que trae autenticación integrada — **no hace falta construirla desde cero**:
- `mcp.auth = BearerTokenProvider({"token": "actor_id", ...})`: mapea tokens estáticos a identidades, con validación automática antes de que el tool handler se ejecute. Para un grupo pequeño y conocido de validadores, probablemente sea suficiente.
- `get_access_token()` / `CurrentAccessToken()` (en `fastmcp.server.dependencies`): dan la identidad ya autenticada dentro de cualquier función — incluido `resolve_actor()`. `get_access_token()` devuelve `None` si no hay sesión autenticada (seguro de llamar sin importar el transporte).
- Dato importante si en algún punto se lee el header crudo en vez de usar `mcp.auth`: `get_http_headers()` excluye `authorization` por defecto, hay que pasar `include_all=True` o `include={"authorization"}` explícitamente.
- Para algo más avanzado a futuro (login federado, JWT, rotación automática): `RemoteAuthProvider` + `JWTVerifier`/`ScalekitProvider`/`AzureJWTVerifier` — innecesario para el alcance actual.
- Hallazgo colateral (bug/gap pre-existente, no introducido por esta épica): `generate_session_token()`/`validate_session_token()` existen hoy en `security.py` y se le indica al operador de `run_http()` que mande un bearer token, pero **nada valida ese token actualmente** — `mcp.run(transport="sse", ...)` se llama sin ningún parámetro de auth. La única protección real hoy es que el server solo escucha en `127.0.0.1`. Esto se reemplaza por completo al configurar `mcp.auth`, no se "arregla" aparte.

## Misiones propuestas (cada una = un change de OpenSpec independiente)

1. **Modelo de credenciales y roles** — decidir dónde vive el mapeo token→actor_id→rol (tabla `actors` simple vs. config estático), reutilizando `LEVEL_HIERARCHY` (read/analyze/write) en vez de inventar roles nuevos: "proposer" ≈ `analyze`, "validator" ≈ `write`.
2. **Configurar `mcp.auth`** en `run_http()` con `BearerTokenProvider` (o el proveedor que salga elegido en la misión 1), reemplazando `generate_session_token()`/`validate_session_token()` (que hoy no hacen nada real).
3. **`resolve_actor()` en modo `shared`** — usa `get_access_token()` en vez de lanzar `NotImplementedError`.
4. **`check_access` basado en rol en modo `shared`** — nueva rama que resuelve el nivel desde el rol del actor autenticado (misión 1), en vez de `MERIDIAN_ACCESS_LEVEL`. Modo local sigue leyendo la variable de entorno exactamente como hoy.
5. **(No bloqueante, después de las anteriores)** Endurecimiento para exposición real en red: rate limiting/anti-spam en `create_pending_proposal`, revisar si el single-writer de SQLite es un problema real — solo si la carga concurrente lo justifica, no antes de medirlo.

Dependencia entre misiones: 1 → 2 → 3 → 4. La 5 es posterior y no bloquea declarar el modo shared "funcional".

## Próximo paso (mañana)

Arrancar con la Misión 1 (`/opsx:new` o `/opsx:ff`), siguiendo el mismo ciclo que `add-actor-identity-tracking`: proposal → specs → design → tasks → apply, con su propio grupo de tests de "no regresión en modo local" como el que ya quedó establecido.
