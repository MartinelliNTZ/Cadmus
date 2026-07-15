# Conversor de Vector a SVG - Guia Rapida

Esta herramienta exporta una capa vectorial de QGIS a SVG, respetando opciones de fondo, borde, rotulo y generacion por entidad.

## Como usar

1. Abra `Cadmus > Conversor de Vector a SVG`.
2. Seleccione la capa vectorial de entrada.
3. Si quiere, active `Solo entidades seleccionadas`.
4. Configure color de fondo, color/grosor del borde y color/tamano del rotulo.
5. Active o desactive fondo transparente, borde, rotulo y generacion de un SVG por entidad.
6. Elija la carpeta de salida o use la carpeta del proyecto.
7. Ejecute la herramienta.

## Lo que el plugin hace realmente

- Valida que la entrada sea una capa vectorial valida con entidades.
- Usa solo las entidades seleccionadas cuando esa opcion esta activa.
- Reproyecta las geometrias a WGS84 antes de construir el SVG.
- Exporta un unico SVG para toda la capa o un SVG por entidad.
- Aplica fondo transparente o color de fondo fijo.
- Controla el borde de las geometrias con el color y grosor definidos por el usuario.
- Intenta dibujar los rotulos reales de la capa a partir de la configuracion de labeling de QGIS, con fallback para `displayExpression()` y campo `Name`.

## Nombres de archivo

- La exportacion unica usa el nombre de la capa de QGIS.
- La exportacion por entidad:
  - usa el campo `Name` si existe y tiene valor;
  - en caso contrario usa `NombreDeLaCapa_1`, `NombreDeLaCapa_2`, `NombreDeLaCapa_3`...
- Si el archivo ya existe, el plugin genera un nombre incremental para no sobrescribirlo.

## Comportamiento importante

- Si `Fondo transparente` esta activo, el SVG no recibe color de fondo.
- Si `Mostrar Borde` esta desactivado, el contorno de las geometrias no se dibuja.
- Si `Mostrar Rotulo` esta desactivado, no se exporta ningun texto.
- El tamano del rotulo puede controlarse directamente en la herramienta.
- El resultado final siempre se guarda en disco, en la carpeta elegida.

## Cuando usarla

Use esta herramienta cuando quiera:

- generar iconos o figuras SVG a partir de vectores del proyecto;
- exportar entidades individualmente para layout, web o automatizacion;
- reutilizar la simbologia basica de la capa en una salida vectorial liviana.

## Cuidados

- Revise la configuracion de labeling de la capa si espera ver rotulos en la salida.
- Las capas con muchas entidades pueden generar muchos archivos cuando la exportacion por entidad esta activa.
- Para obtener nombres mas limpios, conviene completar el campo `Name` antes de exportar un SVG por entidad.
