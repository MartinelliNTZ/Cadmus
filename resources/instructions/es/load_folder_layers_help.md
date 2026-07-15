# Cargar Capas desde Carpeta — Guia Rapida

Esta herramienta recorre una carpeta y sus subcarpetas para cargar archivos vectoriales y raster en el proyecto actual de QGIS.

Tambien puede:

- filtrar por tipo de archivo;
- evitar recargar archivos que ya estan en el proyecto;
- preservar la estructura de carpetas como grupos;
- ignorar la ultima carpeta al crear esos grupos;
- crear una copia de respaldo del proyecto antes de la carga, cuando el proyecto ya fue guardado.

## Como usar

1. Abra `Cadmus > Load Folder Layers`.
2. Elija la carpeta raiz que contiene los archivos.
3. Marque uno o mas tipos de archivo en la seccion `File Types`.
4. Ajuste las opciones extra si es necesario:
- `Load only missing files`: omite archivos que ya estan cargados en el proyecto.
- `Preserve folder structure`: crea grupos en el panel de capas segun las subcarpetas.
- `Do not group last folder`: elimina el ultimo nivel de carpeta antes de crear grupos.
- `Create project backup if saved`: intenta crear un respaldo del proyecto antes de cargar.
5. Ejecute la herramienta.

## Lo que el plugin hace realmente

- Realiza una busqueda recursiva con `os.walk()` en la carpeta seleccionada.
- Filtra los archivos por las extensiones marcadas en la interfaz.
- Trata formatos como `shp`, `gpkg`, `geojson`, `kml`, `csv`, `gpx`, `tab`, `las` y `laz` como datos vectoriales.
- Trata formatos como `tif`, `tiff`, `ecw`, `jp2` y `asc` como datos raster.
- Crea cada capa mediante `ExplorerUtils.create_layer()`.
- Agrega las capas en la raiz del proyecto o en grupos, segun las opciones marcadas.

## Estructura de grupos

- Si `Preserve folder structure` esta desmarcado, todas las capas se agregan a la raiz del proyecto.
- Si esta marcado, el plugin usa la ruta relativa de la carpeta del archivo para construir grupos anidados.
- Si `Do not group last folder` esta activado, el ultimo segmento de carpeta se elimina antes de crear el grupo.
- Cuando la ruta relativa queda como `.` o vacia, la capa se agrega en la raiz del proyecto.

## Comportamiento importante

- Es obligatorio elegir una carpeta valida.
- Es obligatorio marcar al menos un tipo de archivo.
- La opcion de respaldo solo se habilita cuando el proyecto actual ya fue guardado en disco.
- `Load only missing files` compara la ruta normalizada del archivo con las fuentes de las capas ya cargadas.

## Ejecucion sincrona y asincrona

- Hasta 19 archivos, la herramienta se ejecuta de forma sincrona.
- Por encima de 19 archivos, inicia una pipeline asincrona para reducir el impacto en la interfaz.
- En modo asincrono, hay una ventana de progreso propia mientras se agregan las capas.
- Si el usuario cancela, el proceso se detiene en el punto actual y las capas ya agregadas permanecen en el proyecto.

## Cuando usarla

Use esta herramienta cuando necesite cargar muchos archivos desde una carpeta sin agregarlos manualmente uno por uno.

Es especialmente util para:

- proyectos organizados por subcarpetas;
- cargas recurrentes de datos actualizados;
- carpetas con mezcla de vectores y raster.

## Cuidados

- Revise los tipos de archivo marcados antes de ejecutar la herramienta.
- Si quiere mantener organizado el arbol de capas, use `Preserve folder structure`.
- Si la carpeta contiene muchos archivos, espere una carga parcial si cancela a mitad del proceso.
