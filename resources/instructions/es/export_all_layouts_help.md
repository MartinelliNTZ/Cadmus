# Exportar Todos los Layouts — Guia Rapida

Esta herramienta exporta todos los layouts del proyecto actual a PDF, PNG o ambos formatos.

Tambien puede:

- unir todos los PDF exportados en un solo archivo final;
- convertir los PNG exportados en un unico PDF;
- evitar sobrescrituras creando nombres con sufijos;
- guardar las preferencias usadas en la interfaz.

## Como usar

1. Abra `Cadmus > Export All Layouts`.
2. Seleccione al menos un formato de salida: `Export PDF` y/o `Export PNG`.
3. Ajuste las opciones extra si es necesario:
- `Merge PDF`: une los PDF exportados en `_PDF_UNICO_FINAL.pdf`.
- `Merge PNG`: convierte los PNG exportados en un PDF final llamado `_PNG_MERGED_FINAL.pdf`.
- `Replace Existing`: sobrescribe archivos existentes.
- `Max Width`: define el ancho maximo usado en el PDF generado a partir de los PNG.
4. Elija la carpeta de salida.
5. Si quiere usar la carpeta del proyecto, haga clic en el boton que apunta a `.../exports`.
6. Haga clic en `Export`.

## Lo que el plugin hace realmente

- Lee todos los layouts del proyecto actual mediante `layoutManager().layouts()`.
- Crea la carpeta de salida automaticamente si no existe.
- Elimina caracteres invalidos del nombre de cada layout antes de generar los archivos.
- Cuando `Replace Existing` esta desmarcado, crea nombres como `Layout_1`, `Layout_2`, y asi sucesivamente para evitar conflictos.
- Exporta cada layout de forma individual con `QgsLayoutExporter`.
- Muestra una ventana de progreso durante el procesamiento.
- Permite cancelar la exportacion mientras se esta ejecutando.
- Al final, muestra un resumen con exitos, errores y la carpeta de destino.

## Dependencias opcionales

- `PyPDF2` solo se usa si activa la union de PDF.
- `Pillow` solo se usa si activa la union de PNG en PDF.
- Si falta una dependencia, el plugin pide confirmacion para instalarla.
- Si rechaza la instalacion, la exportacion continua sin esa etapa de union.

## Comportamiento importante

- Es obligatorio seleccionar al menos un formato de exportacion.
- El plugin cuenta un layout como exitoso si al menos uno de los formatos seleccionados se exporta correctamente.
- Si un formato falla y el otro funciona, el error tambien aparece en el resumen final.
- Cancelar detiene el bucle en el punto actual; los archivos ya exportados permanecen en la carpeta.

## Cuando usarla

Use esta herramienta cuando necesite exportar rapidamente todos los layouts de un proyecto sin abrirlos y guardarlos uno por uno.

Es especialmente util para:

- entregar un conjunto completo de planos;
- generar revisiones en lote;
- consolidar la salida PDF en un unico archivo final.

## Cuidados

- Revise la carpeta de salida antes de ejecutar la herramienta, sobre todo si `Replace Existing` esta marcado.
- Si hay layouts con nombres parecidos, revise los archivos generados al finalizar.
- Para proyectos grandes, conviene exportar primero sin merge para validar el resultado.
