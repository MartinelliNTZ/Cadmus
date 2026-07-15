# Coordenadas de Drone — Guia Rapida

Esta herramienta lee archivos MRK de drone y genera una capa de puntos con las posiciones registradas durante el vuelo.

Tambien puede crear una linea de trayectoria a partir de esos puntos, enriquecer los registros con metadatos de fotos y guardar los resultados en archivos.

## Como usar

1. Abra `Cadmus > Coordenadas de Drone`.
2. Elija la carpeta que contiene los archivos MRK.
3. Ajuste las opciones si es necesario:
- `Search subfolders`: busca MRK dentro de las subcarpetas.
- `Match photo metadata`: intenta enriquecer los puntos con informacion de imagenes JPG.
4. Si quiere, configure la salida a archivo para puntos y rastro.
5. Si quiere, seleccione archivos QML para aplicar estilo a los puntos y al rastro.
6. Ejecute la herramienta.

## Lo que el plugin hace realmente

- Inicia una pipeline asincrona con `MrkParseStep`.
- Crea una capa de puntos llamada `MRK_Pontos` a partir de los registros leidos.
- Si la opcion de fotos esta activa, tambien ejecuta `PhotoMetadataStep`.
- Puede agregar campos extra como nombre de archivo, fechas, dimensiones de imagen, modelo de camara, ISO, apertura y otros metadatos.
- Genera una capa de linea conectando puntos agrupados por `mrk_path` y `mrk_file`.
- Agrega las capas generadas al proyecto.
- Puede guardar puntos y rastro en archivo con renombrado automatico si el destino ya existe.
- Puede aplicar estilos QML por separado a puntos y rastro cuando la opcion esta habilitada.

## Comportamiento importante

- La herramienta trabaja desde una carpeta, no desde una capa ya cargada.
- La vinculacion con fotos depende de que existan imagenes compatibles en carpetas relacionadas con los archivos MRK.
- Si no se encuentran metadatos de fotos, los puntos aun pueden generarse sin ese enriquecimiento.
- El procesamiento principal se ejecuta en segundo plano.
- Los puntos siempre se generan primero; el rastro se deriva de esos puntos.

## Salidas generadas

- Puntos MRK como capa en memoria o archivo.
- Rastro del vuelo como capa en memoria o archivo.
- Estilo opcional aplicado por separado a puntos y linea.

## Cuando usarla

Use esta herramienta cuando quiera convertir archivos MRK en productos espaciales que puedan visualizarse y analizarse en QGIS.

Es especialmente util para:

- mapear posiciones de fotos del vuelo;
- reconstruir la trayectoria del drone;
- enriquecer los puntos con metadatos tecnicos de imagen.

## Cuidados

- Confirme que la carpeta seleccionada realmente contiene archivos MRK validos.
- Si quiere vincular fotos, mantenga la estructura de carpetas consistente con los datos del vuelo.
- Si quiere resultados persistentes, prefiera guardar en `gpkg`.
