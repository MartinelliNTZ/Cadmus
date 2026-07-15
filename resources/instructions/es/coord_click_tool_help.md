# Capturar Coordenadas — Guia Rapida

Esta herramienta permite hacer clic en el mapa y abrir un panel con informacion detallada del punto seleccionado.

En el mismo flujo de uso, `CoordClickTool` captura el punto y `CoorResultDialog` muestra y actualiza los resultados.

## Como usar

1. Active `Cadmus > Capturar Coordenadas`.
2. Haga clic en cualquier punto del mapa.
3. Vea el dialogo con:
- coordenadas WGS84 en decimal y DMS;
- coordenadas UTM;
- zona, hemisferio y EPSG;
- altitud aproximada;
- direccion aproximada.
4. Use los botones para copiar los bloques de informacion deseados.
5. Haga clic nuevamente en el mapa para actualizar el mismo dialogo con otro punto.

## Lo que el plugin hace realmente

- Captura la coordenada clicada usando snapping cuando existe un snap valido en el canvas.
- Convierte el punto en informacion geografica y UTM.
- Abre el dialogo de resultado en el primer clic y luego reutiliza la misma ventana.
- Inicia una pipeline asincrona con dos tareas en paralelo:
- geocodificacion inversa;
- consulta de altimetria.
- Si la pipeline falla, intenta un fallback con tareas separadas.
- Cancela tareas anteriores cuando el usuario hace clic en otro punto.

## Lo que aparece en el dialogo

- Latitud y longitud en decimal.
- Latitud y longitud en DMS.
- Easting y Northing en UTM.
- Zona, hemisferio y EPSG.
- Altitud aproximada.
- Municipio, region intermedia, estado, region y pais.
- Botones para copiar WGS84, UTM o la ubicacion completa.

## Comportamiento importante

- Las coordenadas basicas aparecen primero; la direccion y la altitud pueden tardar algunos segundos.
- Sin internet, el dialogo sigue mostrando coordenadas, pero puede no completar direccion y altitud.
- El dialogo usa el mismo `ToolKey` que la herramienta de clic, por eso el archivo correcto es `coord_click_tool_help.md`.
- El boton de copiar ubicacion completa envia un resumen de texto al portapapeles.

## Cuando usarla

Use esta herramienta cuando necesite inspeccionar rapidamente un punto del mapa sin crear capa, entidad o anotacion.

Es especialmente util para:

- verificar coordenadas en mas de un sistema;
- obtener altitud aproximada del punto;
- copiar ubicacion en informes, mensajes o documentos.

## Cuidados

- La altitud es aproximada y depende de un servicio externo.
- La direccion depende de la cobertura del servicio de geocodificacion inversa.
- Los clics consecutivos cancelan consultas anteriores y priorizan el punto mas reciente.
