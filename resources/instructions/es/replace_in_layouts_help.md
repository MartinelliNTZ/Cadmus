# Reemplazar Texto en Layouts — Guia Rapida

Esta herramienta busca texto en las etiquetas de los layouts del proyecto y lo reemplaza por un nuevo valor.

En el estado actual del codigo, actua sobre elementos del tipo `QgsLayoutItemLabel`.

## Como usar

1. Abra `Cadmus > Replace Text in Layouts`.
2. Ingrese el texto a buscar.
3. Ingrese el texto nuevo.
4. Si quiere, use el boton de intercambio para invertir ambos campos.
5. Ajuste las opciones:
- `Case Sensitive`: diferencia mayusculas y minusculas.
- `Full Label Replace`: reemplaza todo el texto de la etiqueta cuando encuentra coincidencia.
6. Ejecute la herramienta y confirme la operacion destructiva.

## Lo que el plugin hace realmente

- Guarda en preferencias los ultimos valores ingresados y las opciones marcadas.
- Exige que el campo de busqueda no este vacio.
- Muestra una confirmacion antes de cambiar los layouts.
- Si el proyecto ya esta guardado en disco, crea un respaldo del `.qgz` dentro de la carpeta `backup`.
- Recorre todos los layouts del proyecto.
- Dentro de cada layout, modifica solo los elementos que son `QgsLayoutItemLabel`.
- Al final, muestra un resumen con la cantidad de layouts analizados y cambios aplicados.

## Como funciona el reemplazo

- Con `Case Sensitive` activado, la busqueda respeta mayusculas y minusculas.
- Con `Case Sensitive` desactivado, la busqueda ignora esa diferencia.
- Con `Full Label Replace` desactivado, el plugin hace un reemplazo parcial dentro del texto de la etiqueta.
- Con `Full Label Replace` activado, el plugin reemplaza todo el contenido de la etiqueta por el texto nuevo cuando encuentra coincidencia.

## Comportamiento importante

- La herramienta no modifica otros tipos de elementos de layout; trabaja solo con etiquetas.
- El respaldo solo se crea si el proyecto ya fue guardado.
- Si el proyecto no esta guardado, la herramienta puede ejecutarse igual, pero sin crear respaldo.
- El resumen final informa cantidades, no una lista detallada por elemento.

## Cuando usarla

Use esta herramienta cuando necesite actualizar rapidamente texto repetido en varios layouts del mismo proyecto.

Es especialmente util para:

- cambiar anio, nombre de cliente o responsable;
- actualizar textos estandar en muchos layouts;
- corregir terminos repetidos sin editar etiqueta por etiqueta.

## Cuidados

- Revise bien el texto de busqueda para evitar reemplazos demasiado amplios.
- Use `Full Label Replace` solo cuando quiera sustituir el contenido completo de la etiqueta.
- Si el proyecto es importante, guardelo antes de ejecutar para asegurar la creacion del respaldo.
