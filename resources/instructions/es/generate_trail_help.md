# Generar Rastro de Maquinas — Guia Rapida

Esta herramienta genera la franja ocupada por un implemento a partir de una capa de lineas.

En el flujo actual del codigo, transforma la linea de entrada en un resultado con buffer, usando la mitad del ancho informado como distancia de buffer.

## Como usar

1. Abra `Cadmus > Generar Rastro de Maquinas`.
2. Seleccione la capa de lineas de entrada.
3. Ingrese el tamano del implemento en metros.
4. Si quiere, active la salida a archivo y elija la ruta de destino.
5. Si quiere, seleccione un archivo QML para aplicar estilo al resultado.
6. Ejecute la herramienta.

## Lo que el plugin hace realmente

- Valida que la entrada sea una capa vectorial de lineas.
- Convierte la distancia ingresada en metros a la unidad de la capa.
- Usa `buffer_distance = tamano_del_implemento / 2`.
- Si la opcion de solo seleccionadas esta activa, procesa solo las entidades seleccionadas.
- Ejecuta la pipeline `Explode -> Buffer -> Save`.
- Cuando la salida a archivo esta desactivada, crea la capa final en memoria.
- Cuando la salida a archivo esta activada, guarda en la ruta elegida y renombra automaticamente si el archivo ya existe.
- Agrega la capa final al proyecto si todavia no esta cargada.
- Aplica el estilo QML solo cuando esa opcion esta habilitada y hay un archivo informado.

## Ejecucion sincrona y asincrona

- El plugin consulta la configuracion global `async_threshold_features`.
- Si la capa tiene mas entidades que ese umbral, se ejecuta en una pipeline asincrona.
- Si esta por debajo del umbral, se ejecuta de forma sincrona.
- En ambos casos, el objetivo es generar la misma capa final.

## Comportamiento importante

- El valor del implemento no puede ser `0`.
- La entrada debe ser una capa de lineas.
- El nombre predeterminado del resultado es `Rastro_implemento`.
- El resultado representa la franja generada por un buffer alrededor de las lineas procesadas.
- Si no guarda en archivo, el resultado queda como capa en memoria.

## Cuando usarla

Use esta herramienta cuando quiera representar el ancho de trabajo de un implemento a partir de trayectorias, pasadas o lineas de desplazamiento.

Es especialmente util para:

- crear una franja de cobertura operativa;
- visualizar el ancho ocupado en campo;
- generar un producto vectorial derivado de lineas de recorrido.

## Cuidados

- Revise el CRS de la capa para asegurarse de que la conversion de distancia tenga sentido.
- Como el buffer usa la mitad del ancho informado, confirme que el valor ingresado corresponde al ancho total del implemento.
- Si quiere conservar el resultado, prefiera guardarlo en `gpkg`.
