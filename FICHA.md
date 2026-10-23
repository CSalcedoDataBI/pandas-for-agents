# Ficha — pandas-for-agents

> Ficha NORTE de esta herramienta. La lee su experto (`.claude/agents/experto.md`) en cada PR.
> Guía: [NORTE.md](https://github.com/CSalcedoDataBI/docker-lab/blob/main/NORTE.md).
> Cambiarla exige una nueva aprobación de Cristóbal.

## Qué es

- **Qué construye y para quién:** la referencia de pandas para agentes de IA. Cada función y cada
  método (funciones de primer nivel, `DataFrame`, `Series`, `Index`, `GroupBy`, `Resampler` y los
  accesores `.str`, `.dt`, `.cat`, `.sparse` y `.plot`) sale de la introspección del paquete
  `pandas` instalado, por versión, con su firma, su docstring y la marca de lo deprecado o
  eliminado entre la 2.x y la versión actual, que es la trampa número uno de los agentes. Es para
  quien escribe código de pandas con un agente.
- **Papel** (`repo-roles`): tool (plugin de skills)
- **Gemelo público/privado:** ninguno por ahora. Hermanos de familia: `dax-for-agents`,
  `powerquery-m-for-agents`, `spark-for-agents` y `polars-for-agents`.

## Norte

- **Plan vigente:** [épica v0.1 — catálogo de pandas exportado del motor](https://github.com/CSalcedoDataBI/pandas-for-agents/issues/2)
- **Lo que esta herramienta NO es:**
  - No ejecuta código: es una referencia que un agente lee.
  - No es Polars: eso es `polars-for-agents`.
  - No es un tutorial de pandas ni una guía de rendimiento en Fabric: eso ya lo cubre
    `PatrickGallucci/fabric-skills` (MIT), que se enlaza y no se duplica.

## Zonas protegidas

Lo que no se toca sin un paso del plan que lo nombre:

- El catálogo generado (`catalog/`): solo lo escribe el script de exportación. Un nombre a mano
  rompe la promesa de «ningún nombre inventado».
- `LICENSE` (MIT) y la visibilidad pública del repo.

## Capa y feedback

- **Capa de nodo** (ADR 0023): `etl`
- **Skill de feedback:** `pandas-for-agents:pandas-feedback` (planeada en la v0.1)

## Check y experto

- **Check de CI requerido:** `Validate` (ruleset `main protegida` de `main`)
- **Suite de pruebas:** `python scripts/check_repo.py`
- **Runner:** GitHub (repo público)
- **Formato de tag:** `vX.Y.Z` (release-please)
- **Experto:** `.claude/agents/experto.md`
- **¿Plugin del directorio?:** todavía no. Se envía cuando salga de pre-release; desde entonces,
  `stable` no se toca y publicar sigue R5.
- **Partes visibles que aprueba Cristóbal:** el README de cara al público y la salida de
  pre-release.

## Aprobación

Aprobada:
