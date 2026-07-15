# Multipart Konvertieren - Kurzanleitung

Dieses Werkzeug arbeitet im aktuellen Stand des Plugins auf Multipart-Features und trennt sie in einzelne Features auf.

Mit anderen Worten: Trotz des Namens "In Multipart konvertieren" zerlegt die aktuelle Verarbeitung jede Multipart-Geometrie in einzelne Teile.

## Verwendung

1. Aktivieren Sie einen Vektor-Layer in QGIS.
2. Oeffnen Sie `Cadmus > In Multipart Konvertieren`.
3. Wenn Features ausgewaehlt sind, fragt das Plugin, ob nur die ausgewaehlten verarbeitet werden sollen.
4. Wenn nichts ausgewaehlt ist, fragt das Plugin, ob alle Features des Layers verarbeitet werden sollen.
5. Bestaetigen Sie den Vorgang.
6. Pruefen Sie das Ergebnis im Layer, bevor Sie die Bearbeitungen speichern.

## Was das Werkzeug tatsaechlich macht

- Verarbeitet den aktiven Layer nur, wenn er ein Vektor-Layer mit Features ist.
- Wenn der Layer Multipart-Features besitzt, entfernt es das urspruengliche Feature und erstellt fuer jeden Geometrietypenteil neue einfache Features.
- Kopiert dieselben Attribute des urspruenglichen Features auf jedes neu erzeugte Feature.
- Beruecksichtigt die aktuelle Auswahl, wenn Features ausgewaehlt sind.

## Verhalten bei der Bearbeitung

- Wenn der Layer nicht im Bearbeitungsmodus ist, startet das Plugin die Bearbeitung vor der Verarbeitung.
- Die Aenderungen erfolgen direkt im bestehenden Layer, ohne einen neuen Layer zu erzeugen.
- Der aktuelle Code speichert am Ende nicht automatisch.
- Wenn der Vorgang fehlschlaegt oder abgebrochen wird, fuehrt das Plugin `rollBack()` aus.

## Wichtige Einschraenkungen

- Die aktuelle Routine aendert nur Features, deren Geometrie bereits im Multipart-Format vorliegt.
- Features, die bereits einfach sind, werden nicht veraendert.
- Wenn der Layer nicht als Multipart-Typ definiert ist, kann die Routine enden, ohne etwas zu aendern.
- Der Text der Oberflaeche und der Name des Werkzeugs stimmen noch nicht vollstaendig mit dem tatsaechlichen Verhalten des Codes ueberein.

## Wann man es verwenden sollte

Verwenden Sie dieses Werkzeug, wenn Sie ein Multipart-Feature haben und jeden Teil in ein eigenes Feature umwandeln moechten, ohne die urspruenglichen Attribute zu verlieren.

## Hinweise

- Pruefen Sie nach der Ausfuehrung die endgueltige Anzahl der Features.
- Kontrollieren Sie, ob die Attributduplizierung zu Ihrem Arbeitsablauf passt.
- Speichern Sie den Layer erst, nachdem Sie das Ergebnis validiert haben.
- Wenn der Layer kritisch ist, erstellen Sie vor der Ausfuehrung ein Backup.
