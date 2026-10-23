# pandas-for-agents — diseño inicial

*2026-10-23. Estado: borrador para la épica v0.1.*

## 1. Qué problema resuelve

Un agente que escribe pandas mezcla versiones: usa `DataFrame.append`, `iteritems` o argumentos
que la 2.x deprecó y la 3.x eliminó, e inventa métodos que suenan bien. `dax-for-agents`,
`powerquery-m-for-agents` y `spark-for-agents` resolvieron lo mismo para su motor: el catálogo sale
del motor, no de la memoria. Aquí se repite la receta con pandas.

## 2. Fuente de verdad

| Qué | Cómo se exporta |
|---|---|
| Funciones de primer nivel | introspección de `pandas` (`dir(pandas)`, solo lo público y llamable) |
| `DataFrame`, `Series`, `Index` | sus miembros públicos: métodos, propiedades y accesores |
| `GroupBy` y `Resampler` | `DataFrameGroupBy`, `SeriesGroupBy` y `Resampler` de `pandas.api.typing` (o sus módulos internos, según la versión) |
| Accesores | `.str`, `.dt` (fechas y duraciones), `.cat`, `.sparse` y `.plot` |
| Firma y docstring | `inspect.signature` y la primera línea del docstring de cada miembro |
| Deprecado | la nota `.. deprecated::` del docstring, con su versión |
| Eliminado | la diferencia entre el catálogo de la última 2.x y el de la versión actual |

Cada JSON fija la versión de pandas con la que se generó. La exportación corre con pandas fijado
por versión, en local o en runners de GitHub (repo público, minutos gratis).

## 3. Antes de escribir nada (NORTE R2)

Hecho en el comentario de [docker-lab#38](https://github.com/CSalcedoDataBI/docker-lab/issues/38):

- Para pandas solo hay **guías generales** escritas a mano, sueltas en colecciones grandes
  (`JetBrains/skills` y otras). Ninguna publica un catálogo sacado del propio paquete, por versión,
  con lo deprecado y lo eliminado marcado. Ese es el hueco.
- [`PatrickGallucci/fabric-skills`](https://github.com/PatrickGallucci/fabric-skills) (MIT) trae
  una skill de **rendimiento de pandas en Fabric**. Se **enlaza, no se duplica**: el rendimiento
  queda fuera de esta herramienta. Si alguna vez se toma texto, va con atribución y el commit de
  origen.
- Ejecutar código queda fuera (MCPs y plugins instalados). Polars es `polars-for-agents`.

## 4. Piezas de la v0.1

1. Script de exportación + JSON del catálogo para la última 2.x y para la versión actual.
2. Marcas de deprecado y eliminado, y un check que falla si una ficha nombra algo que no está en
   el catálogo.
3. Notas de trampas y ejemplos por grupo, validados contra el catálogo.
4. Skill `pandas-reference` que lee el catálogo y las notas, y skill `pandas-feedback`.
5. `.claude-plugin/` (plugin.json + marketplace.json) y `PRIVACY.md`.
6. Nodo de la capa `etl` (ADR 0023): `node.json`.

## 5. Salida de pre-release

Cuando las piezas 1–5 estén en `main` y una prueba de invención (como la de
`powerquery-m-for-agents`) muestre la mejora, se quita el aviso de pre-release y se propone a
Cristóbal enviarlo al directorio de plugins.
