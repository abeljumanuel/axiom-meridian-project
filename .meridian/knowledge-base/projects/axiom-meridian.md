## RN-AXIOM-001
**Scope:** project-axiom-meridian
**Categoría:** documentation
**Severidad:** medium
**Aplica a:** axiom-meridian-project/README.md
**Tags:** readme, pull-requests, capstone, documentation
**Fuente:** manual / instrucción del autor, cierre del release 0.1.0 (2026-10-15)
**Regla:** No agregar ni modificar entradas en la sección "7. Pull Requests" del README.md (los slots "Pull Request N — *Pending.*") sin indicación explícita del autor, aunque una tarea pida "agregar el PR #N" o el PR de GitHub con ese número ya esté mergeado. Esos slots corresponden a entregas del capstone con su propio contexto y no equivalen a los números de PR de GitHub (p. ej. el PR #3 de GitHub no es la entrega "Pull Request 3"). Si una tarea parece requerir editar esa sección, déjala intacta y repórtalo como pendiente para el autor.

## RN-AXIOM-002
**Scope:** project-axiom-meridian
**Categoría:** process
**Severidad:** medium
**Aplica a:** axiom-meridian-project (nombres de ramas)
**Tags:** git, branch-naming, workflow
**Fuente:** manual / CONTRIBUTING.md
**Regla:** Nombra cada rama `<tipo>/<NNN>-<descripcion-corta>`: minúsculas, solo a-z, 0-9 y guiones, en inglés, de 2 a 5 palabras, creada desde un `main` actualizado. Tipos permitidos: feat, fix, docs, refactor, test, chore y release (`release/vX.Y.Z`). `NNN` es el número de su TICKET-NNN; las ramas `docs/` y `chore/` pueden omitirlo. Una rama = un propósito = un PR: si el título necesita "y", divídela. Si existe un change de OpenSpec, reutiliza su nombre tras el número (`fix/021-index-advances-id-counters` ↔ `openspec/changes/fix-index-advances-id-counters`). Borra la rama tras el merge.

## RN-AXIOM-003
**Scope:** project-axiom-meridian
**Categoría:** process
**Severidad:** medium
**Aplica a:** axiom-meridian-project (mensajes de commit)
**Tags:** git, commits, conventional-commits, dco
**Fuente:** manual / CONTRIBUTING.md
**Regla:** El asunto de cada commit sigue Conventional Commits, cita el ticket y no supera 70 caracteres, por ejemplo `fix(TICKET-021): advance id_counters on hand-written code index`. Cada commit lleva `Signed-off-by` (`git commit -s`, DCO). El commit lo ejecuta siempre el humano (ver RN-GLOBAL-008): se propone el mensaje, no se ejecuta.

## RN-AXIOM-004
**Scope:** project-axiom-meridian
**Categoría:** process
**Severidad:** high
**Aplica a:** axiom-meridian-project/docs/06-work-tickets.md, axiom-meridian-project/openspec/changes/**
**Tags:** tickets, backlog, openspec, traceability
**Fuente:** manual / CONTRIBUTING.md
**Regla:** Todo trabajo que no sea `docs/` o `chore/` parte de un `TICKET-NNN` registrado en `docs/06-work-tickets.md` con evidencia de una necesidad real (reproducción, reporte de auditoría o historia de usuario). Un ticket sin evidencia queda en estado `Proposed` y no se implementa. La primera línea del `proposal.md` del change de OpenSpec cita el ticket y el ticket enlaza de vuelta al change.

## RN-AXIOM-005
**Scope:** project-axiom-meridian
**Categoría:** process
**Severidad:** high
**Aplica a:** axiom-meridian-project (descripción de pull requests)
**Tags:** pull-requests, review, documentation
**Fuente:** manual / CONTRIBUTING.md
**Regla:** La descripción de todo PR sigue `.github/pull_request_template.md` y debe permitir al revisor decidir sin reconstruir nada: resumen con enlace al ticket y al change de OpenSpec; evidencia (reproducción y resultado antes y después); alcance en ambos sentidos (qué cambia y qué no, con **BREAKING** si altera comportamiento existente); resultados exactos de verificación (comando, pasa/falla y conteos); riesgos y rollback; y una sección "Not verified" honesta. Enlaza los requisitos formales en vez de repetirlos. El mismo PR actualiza `CHANGELOG.md` (Unreleased) y el texto afectado de `CLAUDE.md`/ADR, y deja el ticket en `In review`. El archivado del change de OpenSpec y el paso del ticket a `Done` se hacen al cerrar la release, en un único PR `chore/close-X.Y.Z-release` para todo lo entregado, no por ticket.


## RN-AXIOM-006
**Scope:** project-axiom-meridian
**Categoría:** testing
**Severidad:** high
**Aplica a:** axiom-meridian-project/src/**, axiom-meridian-project/tests/**
**Tags:** regression-testing, pull-requests, benchmarks, invariants
**Fuente:** manual / CONTRIBUTING.md
**Regla:** Un PR no se da por seguro hasta demostrar que no rompe lo existente: (1) nombra los tests nuevos que fallan en `main` y pasan en la rama, para todo fix y no solo los de ADR (extiende RN-GLOBAL-035); (2) corre la suite completa con y sin el extra `rag`, como lo hace el CI; (3) corre `uv run pytest -m benchmark` si toca ids, consultas o indexado, porque `pyproject.toml` excluye los benchmarks por defecto; (4) lista los invariantes de `CLAUDE.md` que toca y cómo se preservan (contadores de id, `write_block`, `shift_offsets_after`, `sync_tags`, `strip_private_tags`, niveles de acceso); (5) lista cualquier cambio en firmas MCP, esquema o migraciones, etiquetas de bloque o comandos CLI; (6) prueba la compatibilidad con una KB existente sobre una copia, nunca sobre la real.

## RN-AXIOM-007
**Scope:** project-axiom-meridian
**Categoría:** process
**Severidad:** medium
**Aplica a:** axiom-meridian-project (tamaño de pull requests)
**Tags:** pull-requests, pr-size, review
**Fuente:** manual / CONTRIBUTING.md
**Regla:** Mide el tamaño de un PR en líneas de código (añadidas más borradas bajo `src/`, `tests/` y `scripts/`, sin lockfiles): S hasta 150, M de 151 a 400 (objetivo), L de 401 a 800 (justifica en la descripción por qué no se divide) y XL más de 800 (divídelo). Más de 15 archivos de código también es señal para dividir. Los tests no dan margen extra, pero declara el reparto entre código y tests. La excepción a XL es solo para cambios mecánicos sin lógica (licencias, renombrados, archivos generados, ramas `release/`), etiquetados como tales y con un comando que permita verificarlos. Declara el tamaño medido en la descripción.

## RN-AXIOM-008
**Scope:** project-axiom-meridian
**Categoría:** quality
**Severidad:** high
**Aplica a:** axiom-meridian-project/src/meridian/tools/*.py, axiom-meridian-project/src/meridian/utils/id_generator.py
**Tags:** id-counters, data-integrity, write-path, regression-testing
**Fuente:** manual / TICKET-021
**Regla:** Toda ruta de escritura que inserte una fila en `rules` o `lessons` con un código que no provenga de `next_rule_code`/`next_lesson_code` (por ejemplo, el indexador atómico con códigos escritos a mano) debe llamar a `id_generator.bump_code_counter(conn, code)` en la misma transacción que el INSERT. Si no lo hace, `id_counters` queda por detrás de la tabla y el siguiente `approve_proposal` de ese scope reasigna un código ocupado y falla con `UNIQUE constraint failed: rules.code` (o `lessons.code`). `seed_id_counters` solo corrige esto al reiniciar el servidor, no en una sesión en curso. Toda ruta nueva de este tipo lleva un test que indexe y apruebe en el mismo proceso, sin reiniciar, y que falle sin la llamada.

## RN-AXIOM-009
**Scope:** project-axiom-meridian
**Categoría:** documentation
**Severidad:** medium
**Aplica a:** axiom-meridian-project/src/meridian/db/**, axiom-meridian-project/README.md, axiom-meridian-project/docs/04-data-model.md
**Tags:** schema, migrations, documentation-drift, data-model
**Fuente:** TICKET-022 / PR #12 y PR #13
**Regla:** Un PR que cambie el esquema de la base de datos (schema.sql o una migración) debe actualizar en el mismo PR la descripción de ese esquema en README.md (sección del modelo de datos) y en docs/04-data-model.md: tablas, columnas, valores permitidos y las respuestas de las herramientas afectadas. Si la documentación se actualiza en una rama distinta, esa rama debe fusionarse después del cambio de esquema y reflejar su estado final, no el anterior.