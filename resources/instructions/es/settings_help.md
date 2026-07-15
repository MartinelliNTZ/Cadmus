# Configuraciones de Cadmus — Guia Rapida

Esta herramienta centraliza preferencias globales usadas por partes del plugin Cadmus.

En el estado actual del codigo, permite:

- elegir el metodo predeterminado de calculo vectorial;
- definir la precision numerica de campos vectoriales;
- definir el umbral de entidades para procesamiento asincrono;
- abrir la carpeta local de preferencias de Cadmus.

## Como usar

1. Abra `Cadmus > Configuracoes Cadmus`.
2. Elija el metodo de calculo vectorial:
- `Elipsoidal`
- `Cartesiano`
- `Ambos`
3. Ajuste la precision de campos vectoriales.
4. Ajuste el umbral asincrono.
5. Haga clic en `Save`.

## Lo que el plugin hace realmente

- Carga las preferencias guardadas con `load_tool_prefs()`.
- Guarda la configuracion bajo la clave de preferencias `settings`.
- Muestra un mensaje de confirmacion despues de guardar.
- Cierra la ventana justo despues de aplicar las preferencias.
- Permite abrir la carpeta local donde se almacenan los archivos de preferencias.

## Significado de cada opcion

- `Metodo de calculo vectorial`: define el texto almacenado en `calculation_method`.
- `Precision de campos vectoriales`: guarda un valor entero en `vector_field_precision`.
- `Umbral asincrono`: guarda un valor entero en `async_threshold_features`.

## Comportamiento importante

- El umbral asincrono actual se mide en numero de entidades, no en MB.
- La precision acepta valores entre 0 y 10.
- El umbral asincrono acepta valores entre 1 y 100000000.
- El codigo aun lee la antigua clave `async_threshold_bytes` por compatibilidad, pero ahora usa el limite por entidades.
- Este plugin solo guarda preferencias; no ejecuta calculos vectoriales por si mismo.

## Carpeta de preferencias

- El enlace de la interfaz intenta abrir `PREF_FOLDER` en el sistema operativo.
- Si la carpeta no existe, el plugin muestra una advertencia en lugar de abrir el explorador de archivos.

## Cuando usarla

Use esta herramienta cuando quiera ajustar el comportamiento predeterminado de otras herramientas de Cadmus que dependen de estas preferencias globales.

## Cuidados

- Cambie el metodo de calculo solo si tiene sentido para su flujo de trabajo.
- Si reduce demasiado el umbral asincrono, mas operaciones pueden pasar a ejecutarse en segundo plano.
- Si nota un comportamiento extrano despues de cambiar preferencias, revise los archivos guardados en la carpeta de preferencias.
