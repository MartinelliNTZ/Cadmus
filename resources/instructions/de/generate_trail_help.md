# Maschinenfahrspur Erzeugen - Kurzanleitung

Dieses Werkzeug erzeugt aus einem Linien-Layer die vom Geraet belegte Flaeche.

Im aktuellen Codefluss wird die Eingabelinie in ein gepuffertes Ergebnis umgewandelt, wobei die Haelfte der angegebenen Breite als Pufferdistanz verwendet wird.

## Verwendung

1. Oeffnen Sie `Cadmus > Maschinenfahrspur Erzeugen`.
2. Waehlen Sie den Eingabe-Linien-Layer.
3. Geben Sie die Geraetebreite in Metern an.
4. Wenn Sie moechten, aktivieren Sie das Speichern in Datei und waehlen Sie den Ausgabepfad.
5. Wenn Sie moechten, waehlen Sie eine QML-Datei, um den Stil auf das Ergebnis anzuwenden.
6. Fuehren Sie das Werkzeug aus.

## Was das Plugin tatsaechlich macht

- Prueft, ob die Eingabe ein Vektor-Layer mit Linien ist.
- Wandelt die eingegebene Distanz von Metern in die Einheit des Layers um.
- Verwendet `buffer_distance = geraetebreite / 2`.
- Wenn die Option fuer nur ausgewaehlte Features aktiv ist, verarbeitet es nur die ausgewaehlten Features.
- Fuehrt die Pipeline `Explode -> Buffer -> Save` aus.
- Wenn kein Speichern in Datei aktiv ist, wird der End-Layer im Speicher erzeugt.
- Wenn das Speichern in Datei aktiv ist, schreibt es in den gewaehlten Pfad und verwendet automatische Umbenennung, falls die Datei bereits existiert.
- Fuegt den End-Layer dem Projekt hinzu, sofern er noch nicht geladen ist.
- Wendet den QML-Stil nur an, wenn diese Option aktiv ist und eine Datei angegeben wurde.

## Synchrone und asynchrone Ausfuehrung

- Das Plugin liest die globale Einstellung `async_threshold_features`.
- Wenn der Layer mehr Features als dieser Grenzwert hat, laeuft die Pipeline asynchron.
- Liegt er darunter, wird synchron verarbeitet.
- In beiden Faellen ist das Ziel, denselben Ergebnis-Layer zu erzeugen.

## Wichtiges Verhalten

- Der Geraetewert darf nicht `0` sein.
- Die Eingabe muss ein Linien-Layer sein.
- Der Standardname des Ergebnisses ist `Rastro_implemento`.
- Das Ergebnis repraesentiert die durch Buffer um die verarbeiteten Linien erzeugte Flaeche.
- Wenn Sie nicht in Datei speichern, bleibt das Ergebnis als Memory-Layer erhalten.

## Wann man es verwenden sollte

Verwenden Sie dieses Werkzeug, wenn Sie die Arbeitsbreite eines Geraets anhand von Fahrspuren, Ueberfahrten oder Bewegungs-Linien darstellen moechten.

Es ist besonders nuetzlich, um:

- eine betriebliche Abdeckungsflaeche zu erzeugen;
- die belegte Breite im Feld zu visualisieren;
- ein aus Fahr-Linien abgeleitetes Vektorprodukt zu generieren.

## Hinweise

- Pruefen Sie das CRS des Layers, damit die Distanzumrechnung sinnvoll ist.
- Da der Buffer die Haelfte der angegebenen Breite verwendet, sollten Sie sicherstellen, dass der eingegebene Wert der Gesamtbreite des Geraets entspricht.
- Wenn Sie das Ergebnis dauerhaft speichern moechten, bevorzugen Sie `gpkg`.
