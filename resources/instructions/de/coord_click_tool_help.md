# Koordinaten Erfassen - Kurzanleitung

Dieses Werkzeug ermoeglicht es, auf die Karte zu klicken und ein Fenster mit detaillierten Informationen zum ausgewaehlten Punkt zu oeffnen.

Im selben Nutzungsfluss erfasst `CoordClickTool` den Punkt und `CoorResultDialog` zeigt die Ergebnisse an und aktualisiert sie.

## Verwendung

1. Aktivieren Sie `Cadmus > Koordinaten Erfassen`.
2. Klicken Sie auf einen beliebigen Punkt der Karte.
3. Im Dialog sehen Sie:
- WGS84-Koordinaten in Dezimalgrad und DMS;
- UTM-Koordinaten;
- Zone, Hemisphaere und EPSG;
- ungefaehre Hoehe;
- ungefaehre Adresse.
4. Verwenden Sie die Schaltflaechen, um die gewuenschten Informationsbloecke zu kopieren.
5. Klicken Sie erneut auf die Karte, um denselben Dialog mit einem neuen Punkt zu aktualisieren.

## Was das Plugin tatsaechlich macht

- Erfasst die angeklickte Koordinate mit Snapping, wenn im Canvas ein gueltiger Snap vorhanden ist.
- Wandelt den Punkt in einen Satz geografischer und UTM-Informationen um.
- Oeffnet beim ersten Mal den Ergebnisdialog und verwendet danach dasselbe Fenster weiter.
- Startet eine asynchrone Pipeline mit zwei parallelen Schritten:
- Reverse-Geocoding;
- Hoehenabfrage.
- Wenn die Pipeline fehlschlaegt, versucht sie einen Fallback mit getrennten Aufgaben.
- Bricht vorherige Aufgaben ab, wenn der Benutzer auf einen anderen Punkt klickt.

## Was im Dialog angezeigt wird

- Breite und Laenge in Dezimalgrad.
- Breite und Laenge in DMS.
- Easting und Northing in UTM.
- Zone, Hemisphaere und EPSG.
- Ungefaehre Hoehe.
- Gemeinde, Zwischenregion, Bundesland, Region und Land.
- Schaltflaechen zum Kopieren von WGS84, UTM oder des vollstaendigen Standorts.

## Wichtiges Verhalten

- Grundlegende Koordinaten erscheinen sofort; Adresse und Hoehe koennen einige Sekunden dauern.
- Ohne Internet zeigt der Dialog weiterhin Koordinaten an, kann aber Adresse und Hoehe eventuell nicht fuellen.
- Der Dialog verwendet denselben `ToolKey` wie das Klick-Werkzeug, daher ist die richtige Hilfe `coord_click_tool_help.md`.
- Die Schaltflaeche zum Kopieren des vollstaendigen Standorts sendet eine Textzusammenfassung in die Zwischenablage.

## Wann man es verwenden sollte

Verwenden Sie dieses Werkzeug, wenn Sie schnell einen Kartenpunkt pruefen moechten, ohne Layer, Feature oder Annotation zu erstellen.

Es ist besonders nuetzlich, um:

- Koordinaten in mehreren Systemen zu pruefen;
- die ungefaehre Hoehe eines Punkts zu erhalten;
- einen Standort fuer Berichte, Nachrichten oder Dokumente zu kopieren.

## Hinweise

- Die Hoehe ist nur ungefaehr und haengt von einem externen Dienst ab.
- Die Adresse haengt von der Abdeckung des Reverse-Geocoding-Dienstes ab.
- Mehrere schnelle Klicks brechen vorherige Abfragen ab und priorisieren den neuesten Punkt.
