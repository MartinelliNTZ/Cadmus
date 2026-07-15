# Copiar Atributos — Guia Rapida

Esta herramienta selecciona campos de una capa de origen y los agrega al esquema de la capa de destino.

Importante: en el estado actual del codigo, no copia valores de las entidades. Solo copia la estructura de campos, con manejo de conflictos de nombre.

## Como usar

1. Abra `Cadmus > Copiar Atributos`.
2. Elija la capa de destino.
3. Elija la capa de origen.
4. Marque los campos deseados de la capa de origen, o use la opcion para todos los campos.
5. Ejecute la herramienta.

## Lo que el plugin hace realmente

- Valida que origen y destino sean capas vectoriales.
- Exige que la capa de destino ya este en modo de edicion.
- Lista los campos segun la capa de origen seleccionada.
- Permite copiar todos los campos o solo los seleccionados.
- Para cada campo elegido:
- si el campo no existe en el destino, se crea;
- si el campo ya existe, el plugin pide una accion para resolver el conflicto.

## Manejo de conflictos

- `skip`: ignora el campo que ya existe.
- `rename`: crea un nuevo campo con un sufijo como `_1`, `_2`, y asi sucesivamente.
- `cancel`: detiene la operacion.

## Comportamiento importante

- La herramienta no transfiere valores entre entidades.
- Tampoco realiza correspondencia espacial ni por clave entre registros.
- El resultado principal es un cambio en el esquema de atributos de la capa de destino.
- Si no se selecciona ningun campo y la opcion de todos los campos no esta activa, la operacion no continua.

## Cuando usarla

Use esta herramienta cuando quiera preparar la capa de destino con nuevos campos basados en la estructura de otra capa.

Es especialmente util para:

- estandarizar esquemas de atributos;
- crear campos faltantes antes de otra etapa de procesamiento;
- replicar nombres y tipos de campos desde una capa modelo.

## Cuidados

- Ponga la capa de destino en modo de edicion antes de ejecutar.
- Si necesitaba copiar valores, esta herramienta aun no lo hace en el codigo actual.
- Revise bien los conflictos de nombre para no crear campos duplicados innecesarios.
