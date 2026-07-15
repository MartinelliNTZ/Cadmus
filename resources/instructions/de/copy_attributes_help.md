# Attribute Kopieren - Kurzanleitung

Dieses Werkzeug waehlt Felder aus einem Quell-Layer aus und fuegt sie der Feldstruktur des Ziel-Layers hinzu.

Wichtig: Im aktuellen Stand des Codes werden keine Feature-Werte kopiert. Es wird nur die Feldstruktur mit Behandlung von Namenskonflikten uebernommen.

## Verwendung

1. Oeffnen Sie `Cadmus > Attribute Kopieren`.
2. Waehlen Sie den Ziel-Layer.
3. Waehlen Sie den Quell-Layer.
4. Markieren Sie die gewuenschten Felder des Quell-Layers oder verwenden Sie die Option fuer alle Felder.
5. Fuehren Sie das Werkzeug aus.

## Was das Plugin tatsaechlich macht

- Prueft, ob Quelle und Ziel gueltige Vektorlayer sind.
- Verlangt, dass sich der Ziel-Layer bereits im Bearbeitungsmodus befindet.
- Listet die Felder auf Basis des ausgewaehlten Quell-Layers auf.
- Erlaubt das Kopieren aller Felder oder nur der ausgewaehlten Felder.
- Fuer jedes ausgewaehlte Feld:
- wenn das Feld im Ziel nicht existiert, wird es erstellt;
- wenn das Feld bereits existiert, fragt das Plugin nach einer Konfliktaktion.

## Behandlung von Konflikten

- `skip`: ueberspringt das bereits vorhandene Feld.
- `rename`: erstellt ein neues Feld mit Suffix wie `_1`, `_2` usw.
- `cancel`: bricht den Vorgang ab.

## Wichtiges Verhalten

- Das Werkzeug uebertraegt keine Werte zwischen Features.
- Es fuehrt auch keine raeumliche oder schluesselbasierte Zuordnung zwischen Datensaetzen durch.
- Das Hauptergebnis ist die Aenderung des Attributschemas des Ziel-Layers.
- Wenn kein Feld ausgewaehlt ist und die Option fuer alle Felder nicht aktiv ist, wird der Vorgang nicht fortgesetzt.

## Wann man es verwenden sollte

Verwenden Sie dieses Werkzeug, wenn Sie den Ziel-Layer mit neuen Feldern vorbereiten moechten, die auf der Struktur eines anderen Layers basieren.

Es ist besonders nuetzlich, um:

- Attributschemata zu standardisieren;
- fehlende Felder vor einem weiteren Verarbeitungsschritt zu erstellen;
- Feldnamen und Feldtypen eines Modell-Layers zu uebernehmen.

## Hinweise

- Versetzen Sie den Ziel-Layer vor dem Ausfuehren in den Bearbeitungsmodus.
- Wenn Sie Werte kopieren wollten, tut dieses Werkzeug das im aktuellen Code noch nicht.
- Pruefen Sie Namenskonflikte sorgfaeltig, damit keine unnoetigen Duplikate entstehen.
