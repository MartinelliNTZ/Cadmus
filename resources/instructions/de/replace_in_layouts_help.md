# Text In Layouts Ersetzen - Kurzanleitung

Dieses Werkzeug sucht Text in Labels der Projekt-Layouts und ersetzt ihn durch den angegebenen neuen Wert.

Im aktuellen Stand des Codes arbeitet es mit Elementen vom Typ `QgsLayoutItemLabel`.

## Verwendung

1. Oeffnen Sie `Cadmus > Replace Text in Layouts`.
2. Fuellen Sie den zu suchenden Text aus.
3. Fuellen Sie den neuen Text aus.
4. Wenn Sie moechten, verwenden Sie die Tausch-Schaltflaeche, um die beiden Felder umzudrehen.
5. Passen Sie die Optionen an:
- `Case Sensitive`: unterscheidet Gross- und Kleinschreibung.
- `Full Label Replace`: ersetzt den gesamten Text des Labels, wenn eine Uebereinstimmung vorliegt.
6. Fuehren Sie das Werkzeug aus und bestaetigen Sie den destruktiven Vorgang.

## Was das Plugin tatsaechlich macht

- Speichert die zuletzt eingegebenen Werte und aktivierten Optionen in den Einstellungen.
- Verlangt, dass das Suchfeld nicht leer ist.
- Zeigt vor der Aenderung der Layouts eine Bestaetigung an.
- Wenn das Projekt auf der Festplatte gespeichert ist, erstellt es ein Backup der `.qgz`-Datei im Ordner `backup`.
- Durchlaeuft alle Layouts des Projekts.
- Innerhalb jedes Layouts aendert es nur Elemente vom Typ `QgsLayoutItemLabel`.
- Am Ende zeigt es eine Zusammenfassung mit Anzahl der geprueften Layouts und der vorgenommenen Aenderungen.

## Wie der Ersatz funktioniert

- Mit aktivem `Case Sensitive` beachtet die Suche Gross- und Kleinschreibung.
- Mit deaktiviertem `Case Sensitive` ignoriert die Suche diesen Unterschied.
- Mit deaktiviertem `Full Label Replace` fuehrt das Plugin einen teilweisen Ersatz innerhalb des Label-Texts aus.
- Mit aktiviertem `Full Label Replace` ersetzt das Plugin den gesamten Inhalt des Labels durch den neuen Text, sobald eine Uebereinstimmung gefunden wird.

## Wichtiges Verhalten

- Das Werkzeug aendert keine anderen Layout-Elementtypen; es arbeitet nur mit Labels.
- Das Backup wird nur erstellt, wenn das Projekt bereits gespeichert wurde.
- Wenn das Projekt nicht gespeichert ist, kann das Werkzeug trotzdem laufen, jedoch ohne Backup-Erstellung.
- Die Abschlusszusammenfassung zeigt die Anzahl der Aenderungen, nicht eine detaillierte Liste pro Element.

## Wann man es verwenden sollte

Verwenden Sie dieses Werkzeug, wenn Sie wiederkehrende Texte in mehreren Layouts desselben Projekts schnell aktualisieren muessen.

Es ist besonders nuetzlich, um:

- Jahr, Kundenname oder verantwortliche Person zu ersetzen;
- standardisierte Texte in mehreren Layouts zu aktualisieren;
- wiederholte Begriffe zu korrigieren, ohne Label fuer Label zu bearbeiten.

## Hinweise

- Pruefen Sie den Suchtext sorgfaeltig, um zu breite Ersetzungen zu vermeiden.
- Verwenden Sie `Full Label Replace` nur, wenn Sie den gesamten Label-Inhalt ersetzen moechten.
- Wenn das Projekt wichtig ist, speichern Sie es vor der Ausfuehrung, damit das Backup sicher erzeugt wird.
