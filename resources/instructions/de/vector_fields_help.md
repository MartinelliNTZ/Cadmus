# Vektorfelder Berechnen - Kurzanleitung

Kurz: Berechnet Koordinatenfelder (X, Y) fuer Punkte, Laenge fuer Linien und Flaeche fuer Polygone, mit Unterstuetzung fuer verschiedene Koordinatensysteme.

---

## Schritt fuer Schritt

1. Oeffnen Sie: Menue -> **Cadmus** -> **Vektorfelder Berechnen**
2. Waehlen Sie den **Vektor-Layer** aus, also Punkte, Linien oder Polygone.
3. Optional koennen Sie in **Einstellungen** festlegen:
   - **Berechnungsmethode**: Ellipsoidal, Cartesian oder Both.
   - **Genauigkeit**: Anzahl der Dezimalstellen, Standard ist 2.
4. Klicken Sie auf **Ausfuehren**. Die Verarbeitung laeuft im Hintergrund und neue Felder werden automatisch hinzugefuegt.

---

## Was im Hintergrund passiert

- **Punkte**: Erstellt die Felder `X` und `Y` mit den Punktkoordinaten.
- **Linien**: Erstellt das Feld `Length` oder `Length_Ellip` / `Length_Cart` mit der Linienlaenge.
- **Polygone**: Erstellt das Feld `Area` oder `Area_Ellip` / `Area_Cart` mit der Polygonflaeche.
- **Verarbeitung**: Bei Layern mit weniger als 1000 Features laeuft die Verarbeitung schnell und synchron; ab 1000 Features asynchron, damit die Oberflaeche nicht blockiert.
- **Geografisches CRS**: Wenn der Layer ein CRS in Grad verwendet, zum Beispiel EPSG:4326, und Sie `Cartesian` waehlen, stellt das Plugin automatisch auf `Both` um, um Ergebnisse in Gradquadrat zu vermeiden.

---

## Schnelle Tipps

- **CRS in Grad?** Reprojizieren Sie in ein metrisches CRS, zum Beispiel UTM, um praezise Ergebnisse in Metern zu erhalten.
- **Methode `Both`**: Erstellt zwei Felder, ellipsoidal und kartesisch. Das ist fuer Vergleichsanalysen nuetzlich.
- **Genauigkeit 0**: Liefert ganzzahlige Werte ohne Dezimalstellen.
- Der Layer bleibt im Bearbeitungsmodus, sodass Sie die Ergebnisse vor dem Speichern pruefen koennen.

---

## Haeufige Probleme und Loesungen

- **Sehr grosse oder seltsame Werte** -> Pruefen Sie das CRS des Layers. Wenn es in Grad ist, reprojizieren Sie ihn.
- **"Layer nicht editierbar"** -> Der Layer ist gesperrt. Entsperren Sie ihn und versuchen Sie es erneut.
- **Werte in Gradquadrat bei Flaeche oder Laenge** -> Sie haben `Cartesian` in einem geografischen CRS gewaehlt. Das Plugin warnt davor, aber Sie koennen es ignorieren.
- **Langsame Verarbeitung bei 10k+ Features** -> Das ist normal. Die asynchrone Verarbeitung funktioniert und der Fortschrittsbalken zeigt den Status.

---

## Schnelle Checkliste nach der Ausfuehrung

- Wurden neue Felder im Layer erstellt?
- Sind die Werte in einer Stichprobe korrekt?
- Entspricht die Genauigkeit den Erwartungen?
- Wurden die Daten gespeichert, falls noetig?

---

## Einstellungen und Support

- Oeffnen Sie **Cadmus Einstellungen**, um Folgendes anzupassen:
  - die Standard-**Berechnungsmethode**;
  - die Standard-**Genauigkeit** fuer neue Felder;
  - den **asynchronen Grenzwert**, ab dem die Verarbeitung asynchron wird.
- Die Einstellungen werden gespeichert und bei spaeteren Ausfuehrungen automatisch angewendet.
- Im Fehlerfall oeffnen Sie das Log-Panel des Plugins und melden Sie Geometrietyp, Anzahl der Features und CRS des Layers.
