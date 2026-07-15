# Drohnenkoordinaten - Kurzanleitung

Dieses Werkzeug liest MRK-Dateien einer Drohne und erzeugt einen Punkt-Layer mit den waehrend des Flugs aufgezeichneten Positionen.

Es kann ausserdem eine Fluglinie aus diesen Punkten erstellen, die Eintraege mit Fotometadaten abgleichen und die Ergebnisse in Dateien speichern.

## Verwendung

1. Oeffnen Sie `Cadmus > Drohnenkoordinaten`.
2. Waehlen Sie den Ordner, der die MRK-Dateien enthaelt.
3. Passen Sie die Optionen bei Bedarf an:
- `Unterordner durchsuchen`: sucht MRKs auch in Unterordnern.
- `Mit Fotometadaten abgleichen`: versucht, die Punkte mit Informationen aus JPG-Bildern anzureichern.
4. Wenn Sie moechten, konfigurieren Sie das Speichern der Punkte und der Flugspur in Dateien.
5. Wenn Sie moechten, waehlen Sie QML-Dateien aus, um Stil auf Punkte und Spur anzuwenden.
6. Fuehren Sie das Werkzeug aus.

## Was das Plugin tatsaechlich macht

- Startet eine asynchrone Pipeline mit `MrkParseStep`.
- Erstellt aus den gelesenen Eintraegen einen Punkt-Layer namens `MRK_Pontos`.
- Wenn die Foto-Option aktiv ist, fuehrt es zusaetzlich `PhotoMetadataStep` aus.
- Kann zusaetzliche Felder wie Dateiname, Daten, Bildgroesse, Kamera, ISO, Blende und weitere Metadaten hinzufuegen.
- Erzeugt einen Linien-Layer, der die Punkte nach Gruppen von `mrk_path` und `mrk_file` verbindet.
- Fuegt die erzeugten Layer dem Projekt hinzu.
- Kann Punkte und Spur in Dateien speichern und dabei automatisch umbenennen, falls das Ziel bereits existiert.
- Kann QML-Stile auf Punkte und Spur anwenden, wenn diese Option aktiviert ist.

## Wichtiges Verhalten

- Das Werkzeug arbeitet mit einem Ordner, nicht mit einem bereits geladenen Layer.
- Der Abgleich mit Fotos setzt voraus, dass in den zugehoerigen MRK-Ordnern passende Bilder vorhanden sind.
- Wenn keine Fotometadaten gefunden werden, koennen die Punkte dennoch ohne diese Anreicherung erstellt werden.
- Die Hauptverarbeitung laeuft im Hintergrund.
- Die Punkte werden immer zuerst erzeugt; die Spur wird aus diesen Punkten abgeleitet.

## Erzeugte Ausgaben

- MRK-Punkte als Memory-Layer oder Datei.
- Flugspur als Memory-Layer oder Datei.
- Optionaler Stil, der getrennt auf Punkte und Linie angewendet wird.

## Wann man es verwenden sollte

Verwenden Sie dieses Werkzeug, wenn Sie MRK-Dateien in raeumliche Produkte umwandeln moechten, die in QGIS visualisiert und analysiert werden koennen.

Es ist besonders nuetzlich, um:

- die Positionen der Flugfotos zu kartieren;
- die Route der Drohne zu rekonstruieren;
- die Punkte mit technischen Bilddaten anzureichern.

## Hinweise

- Stellen Sie sicher, dass der ausgewaehlte Ordner wirklich gueltige MRK-Dateien enthaelt.
- Wenn Sie den Fotoabgleich verwenden moechten, halten Sie die Ordnerstruktur konsistent mit dem Flug.
- Wenn Sie die Ergebnisse dauerhaft speichern wollen, bevorzugen Sie `gpkg`.
