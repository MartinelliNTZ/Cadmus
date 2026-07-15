# Cadmus Einstellungen - Kurzanleitung

Dieses Werkzeug buendelt globale Einstellungen, die von Teilen des Cadmus-Plugins verwendet werden.

Im aktuellen Stand des Codes erlaubt es:

- die Standardmethode fuer Vektorberechnungen zu waehlen;
- die numerische Genauigkeit von Vektorfeldern festzulegen;
- den Feature-Grenzwert fuer asynchrone Verarbeitung festzulegen;
- den lokalen Cadmus-Einstellungsordner zu oeffnen.

## Verwendung

1. Oeffnen Sie `Cadmus > Cadmus Einstellungen`.
2. Waehlen Sie die Methode fuer Vektorberechnungen:
- `Ellipsoidal`
- `Cartesian`
- `Both`
3. Passen Sie die Genauigkeit der Vektorfelder an.
4. Passen Sie den asynchronen Grenzwert an.
5. Klicken Sie auf `Speichern`.

## Was das Plugin tatsaechlich macht

- Laedt gespeicherte Einstellungen mit `load_tool_prefs()`.
- Speichert die Konfiguration im Einstellungsbereich mit dem Schluessel `settings`.
- Zeigt nach dem Speichern eine Bestaetigungsmeldung an.
- Schliesst das Fenster kurz nach dem Anwenden der Einstellungen.
- Ermoeglicht das Oeffnen des lokalen Ordners, in dem die Einstellungsdateien gespeichert werden.

## Bedeutung jeder Option

- `Methode fuer Vektorberechnungen`: definiert den Textwert der Einstellung `calculation_method`.
- `Genauigkeit von Vektorfeldern`: speichert einen ganzzahligen Wert in `vector_field_precision`.
- `Asynchroner Grenzwert`: speichert einen ganzzahligen Wert in `async_threshold_features`.

## Wichtiges Verhalten

- Der aktuelle asynchrone Grenzwert wird in Anzahl der Features gemessen, nicht in MB.
- Der Code akzeptiert Genauigkeitswerte zwischen 0 und 10.
- Der asynchrone Grenzwert akzeptiert Werte von 1 bis 100000000.
- Es gibt Rueckwaertskompatibilitaet beim Lesen des alten Schluessels `async_threshold_bytes`, aber nach dem Laden verwendet das Plugin den Grenzwert in Features.
- Dieses Werkzeug speichert nur Einstellungen; es fuehrt selbst keine Vektorberechnungen aus.

## Einstellungsordner

- Der Link in der Oberflaeche versucht, den Ordner `PREF_FOLDER` im Betriebssystem zu oeffnen.
- Wenn der Ordner nicht existiert, zeigt das Plugin eine Warnung anstatt den Explorer zu oeffnen.

## Wann man es verwenden sollte

Verwenden Sie dieses Werkzeug, wenn Sie das Standardverhalten anderer Cadmus-Werkzeuge anpassen moechten, die von diesen globalen Einstellungen abhaengen.

## Hinweise

- Aendern Sie die Berechnungsmethode nur, wenn sie zu Ihrem Arbeitsablauf passt.
- Wenn Sie den asynchronen Grenzwert zu stark senken, werden mehr Vorgaenge im Hintergrund ausgefuehrt.
- Wenn nach einer Einstellungsaenderung merkwuerdiges Verhalten auftritt, lohnt sich ein Blick in die gespeicherten Dateien im Einstellungsordner.
