# Vector To SVG Konverter - Kurzanleitung

Dieses Werkzeug exportiert einen QGIS-Vektorlayer nach SVG und berucksichtigt Optionen fur Hintergrund, Rand, Beschriftung und Export pro Feature.

## Verwendung

1. Offnen Sie `Cadmus > Vector To SVG Konverter`.
2. Wahlen Sie den Eingabe-Vektorlayer.
3. Aktivieren Sie bei Bedarf `Nur ausgewahlte Features`.
4. Konfigurieren Sie Hintergrundfarbe, Randfarbe/-starke sowie Beschriftungsfarbe/-grosse.
5. Aktivieren oder deaktivieren Sie transparenten Hintergrund, Rand, Beschriftung und den Export eines SVG pro Feature.
6. Wahlen Sie den Ausgabeordner oder verwenden Sie den Projektordner.
7. Fuhren Sie das Werkzeug aus.

## Was das Plugin tatsachlich macht

- Prufung, ob die Eingabe ein gultiger Vektorlayer mit Features ist.
- Verwendet nur ausgewahlte Features, wenn diese Option aktiv ist.
- Reprojiziert die Geometrien nach WGS84, bevor das SVG erstellt wird.
- Exportiert entweder ein einzelnes SVG fur den gesamten Layer oder ein SVG pro Feature.
- Verwendet entweder transparenten Hintergrund oder eine feste Hintergrundfarbe.
- Steuert die Geometrie-Rander mit der vom Benutzer definierten Farbe und Starke.
- Versucht echte Layer-Beschriftungen aus den QGIS-Labeling-Einstellungen zu zeichnen, mit Fallback auf `displayExpression()` und das Feld `Name`.

## Dateibenennung

- Beim Einzel-SVG-Export wird der Name des QGIS-Layers verwendet.
- Beim Export pro Feature:
  - wird das Feld `Name` verwendet, wenn es existiert und einen Wert hat;
  - andernfalls wird `LayerName_1`, `LayerName_2`, `LayerName_3`... verwendet.
- Wenn eine Datei bereits existiert, erstellt das Plugin einen inkrementellen Namen statt sie zu uberschreiben.

## Wichtiges Verhalten

- Wenn `Transparenter Hintergrund` aktiviert ist, wird keine Hintergrundflache in das SVG geschrieben.
- Wenn `Rand anzeigen` deaktiviert ist, werden die Umrisse der Geometrien nicht gezeichnet.
- Wenn `Beschriftung anzeigen` deaktiviert ist, wird kein Text exportiert.
- Die Grosse der Beschriftung kann direkt im Werkzeug gesteuert werden.
- Das Ergebnis wird immer im ausgewahlten Ordner auf die Festplatte geschrieben.

## Wann man es verwenden sollte

Verwenden Sie dieses Werkzeug, wenn Sie:

- SVG-Symbole oder Grafiken aus Projektvektoren erzeugen wollen;
- Features einzeln fur Layout, Web oder Automatisierung exportieren wollen;
- eine einfache Layersymbolik in einer leichten Vektorausgabe wiederverwenden wollen.

## Hinweise

- Uberprufen Sie die Layer-Beschriftung, wenn Sie erwarten, dass Beschriftungen erscheinen.
- Layer mit vielen Features konnen sehr viele Dateien erzeugen, wenn der Export pro Feature aktiviert ist.
- Fur sauberere Dateinamen empfiehlt es sich, das Feld `Name` vor dem Export eines SVG pro Feature zu fullen.
