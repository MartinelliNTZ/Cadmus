# Layer Aus Ordner Laden - Kurzanleitung

Dieses Werkzeug durchsucht einen Ordner und seine Unterordner, um Vektor- und Rasterdateien in das QGIS-Projekt zu laden.

Es kann ausserdem:

- nach Dateitypen filtern;
- vermeiden, Dateien erneut zu laden, die bereits im Projekt vorhanden sind;
- die Ordnerstruktur als Gruppen beibehalten;
- den letzten Ordner bei der Erstellung dieser Gruppen ignorieren;
- vor dem Laden ein Backup des Projekts erstellen, wenn das Projekt bereits gespeichert wurde.

## Verwendung

1. Oeffnen Sie `Cadmus > Load Folder Layers`.
2. Waehlen Sie den Wurzelordner mit den Dateien.
3. Aktivieren Sie einen oder mehrere Dateitypen im Abschnitt `File Types`.
4. Passen Sie bei Bedarf die zusaetzlichen Optionen an:
- `Load only missing files`: ignoriert Dateien, die bereits im Projekt geladen sind.
- `Preserve folder structure`: erzeugt Gruppen im Layer-Panel auf Basis der Unterordner.
- `Do not group last folder`: entfernt die letzte Ordnerstufe beim Erzeugen der Gruppen.
- `Create project backup if saved`: versucht vor dem Vorgang ein Projekt-Backup zu erstellen.
5. Fuehren Sie das Werkzeug aus.

## Was das Plugin tatsaechlich macht

- Fuehrt eine rekursive Suche mit `os.walk()` im ausgewaehlten Ordner durch.
- Filtert Dateien anhand der in der Oberflaeche markierten Erweiterungen.
- Behandelt Formate wie `shp`, `gpkg`, `geojson`, `kml`, `csv`, `gpx`, `tab`, `las` und `laz` als Vektor.
- Behandelt Formate wie `tif`, `tiff`, `ecw`, `jp2` und `asc` als Raster.
- Erstellt jeden Layer mit `ExplorerUtils.create_layer()`.
- Fuegt die Layer je nach aktivierter Option im Projektstamm oder in Gruppen hinzu.

## Gruppenstruktur

- Wenn `Preserve folder structure` deaktiviert ist, werden alle Layer im Projektstamm hinzugefuegt.
- Wenn es aktiviert ist, verwendet das Plugin den relativen Ordnerpfad der Datei, um verschachtelte Gruppen zu erzeugen.
- Wenn `Do not group last folder` aktiv ist, wird das letzte Ordnersegment vor dem Erzeugen der Gruppe entfernt.
- Wenn der relative Pfad zu `.` oder leer wird, wird der Layer im Projektstamm hinzugefuegt.

## Wichtiges Verhalten

- Es ist zwingend erforderlich, einen gueltigen Ordner auszuwaehlen.
- Es ist zwingend erforderlich, mindestens einen Dateityp zu markieren.
- Die Backup-Option ist nur aktiv, wenn das aktuelle Projekt bereits auf der Festplatte gespeichert wurde.
- Der Filter `Load only missing files` vergleicht den normalisierten Dateipfad mit den Quellen bereits geoeffneter Layer.

## Synchrone und asynchrone Ausfuehrung

- Bis zu 19 Dateien laeuft das Werkzeug synchron.
- Ab mehr als 19 Dateien startet es eine asynchrone Pipeline, um die Oberflaeche weniger zu belasten.
- Im asynchronen Modus gibt es ein eigenes Fortschrittsfenster fuer das Hinzufuegen der Layer.
- Wenn der Benutzer abbricht, stoppt der Vorgang an der aktuellen Stelle und bereits hinzugefuegte Layer bleiben im Projekt.

## Wann man es verwenden sollte

Verwenden Sie dieses Werkzeug, wenn Sie viele Dateien aus einem Ordner laden muessen, ohne Layer fuer Layer manuell hinzuzufuegen.

Es ist besonders nuetzlich fuer:

- Projekte, die nach Unterordnern organisiert sind;
- wiederkehrende Ladevorgaenge aktualisierter Daten;
- Ordner mit einer Mischung aus Vektor- und Rasterdaten.

## Hinweise

- Pruefen Sie vor der Ausfuehrung die markierten Dateitypen.
- Wenn Sie die Baumstruktur organisiert halten wollen, verwenden Sie `Preserve folder structure`.
- Wenn der Ordner sehr viele Dateien enthaelt, rechnen Sie bei Abbruch mit einer teilweisen Ladung.
