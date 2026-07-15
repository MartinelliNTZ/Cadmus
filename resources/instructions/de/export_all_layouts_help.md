# Alle Layouts Exportieren - Kurzanleitung

Dieses Werkzeug exportiert alle Layouts des aktuellen Projekts als PDF, PNG oder in beiden Formaten.

Es kann ausserdem:

- alle exportierten PDFs zu einer einzigen Datei zusammenfuegen;
- exportierte PNGs in ein einzelnes PDF umwandeln;
- Ueberschreiben vermeiden, indem Namen mit Suffixen erzeugt werden;
- die in der Oberflaeche verwendeten Einstellungen speichern.

## Verwendung

1. Oeffnen Sie `Cadmus > Export All Layouts`.
2. Aktivieren Sie mindestens ein Ausgabeformat: `Export PDF` und/oder `Export PNG`.
3. Passen Sie bei Bedarf die zusaetzlichen Optionen an:
- `Merge PDF`: fuegt die exportierten PDFs in `_PDF_UNICO_FINAL.pdf` zusammen.
- `Merge PNG`: wandelt die exportierten PNGs in ein finales PDF namens `_PNG_MERGED_FINAL.pdf` um.
- `Replace Existing`: ueberschreibt vorhandene Dateien.
- `Max Width`: definiert die maximale Breite im aus PNGs erzeugten PDF.
4. Waehlen Sie den Ausgabeordner.
5. Wenn Sie den Projektordner verwenden moechten, klicken Sie auf die Schaltflaeche, die auf `.../exports` verweist.
6. Klicken Sie auf `Export`.

## Was das Plugin tatsaechlich macht

- Liest alle Layouts des aktuellen Projekts ueber `layoutManager().layouts()`.
- Erstellt den Ausgabeordner automatisch, falls er nicht existiert.
- Bereinigt ungueltige Zeichen aus jedem Layoutnamen, bevor Dateien erzeugt werden.
- Wenn `Replace Existing` deaktiviert ist, erstellt es Namen wie `Layout_1`, `Layout_2` usw., um Konflikte zu vermeiden.
- Exportiert jedes Layout einzeln mit `QgsLayoutExporter`.
- Zeigt waehrend der Verarbeitung ein Fortschrittsfenster an.
- Erlaubt es, den Export waehrend des Vorgangs abzubrechen.
- Zeigt am Ende eine Zusammenfassung mit Erfolgen, Fehlern und Zielordner an.

## Optionale Abhaengigkeiten

- `PyPDF2` wird nur verwendet, wenn Sie das Zusammenfuegen von PDFs aktivieren.
- `Pillow` wird nur verwendet, wenn Sie das Zusammenfuegen von PNGs zu PDF aktivieren.
- Wenn eine Abhaengigkeit fehlt, bittet das Plugin um Bestaetigung zur Installation.
- Wenn Sie die Installation ablehnen, laeuft der Export ohne den entsprechenden Merge-Schritt weiter.

## Wichtiges Verhalten

- Es muss mindestens ein Exportformat ausgewaehlt sein.
- Das Plugin zaehlt ein Layout als Erfolg, wenn mindestens eines der gewaehlten Formate erfolgreich exportiert wurde.
- Wenn ein Layout in einem Format fehlschlaegt und im anderen funktioniert, erscheint der Fehler in der Abschlusszusammenfassung.
- Ein Abbruch stoppt die Schleife an der aktuellen Stelle; bereits exportierte Dateien bleiben im Ordner erhalten.

## Wann man es verwenden sollte

Verwenden Sie dieses Werkzeug, wenn Sie schnell alle Layouts eines Projekts exportieren muessen, ohne jedes einzeln zu oeffnen und zu speichern.

Es ist besonders nuetzlich, um:

- einen vollstaendigen Satz Plaene zu liefern;
- Serienexporte fuer Revisionen zu erzeugen;
- PDF-Ausgaben in einer einzigen Enddatei zu konsolidieren.

## Hinweise

- Pruefen Sie vor der Ausfuehrung den Ausgabeordner, besonders wenn `Replace Existing` aktiviert ist.
- Wenn Layouts aehnliche Namen haben, kontrollieren Sie nach dem Export die erzeugten Dateien.
- Bei grossen Projekten kann es sinnvoll sein, zuerst ohne Merge zu exportieren, um das Ergebnis zu validieren.
