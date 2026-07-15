# Projekt Speichern, Schliessen und Neu Oeffnen - Benutzerhandbuch

Werkzeug aus dem Paket **Cadmus**, um **QGIS mit dem aktuellen Projekt** automatisch neu zu starten.

---

## Was dieses Werkzeug macht

Dieses Werkzeug ermoeglicht:

- das **automatische Speichern des Projekts** bei vorhandenen Aenderungen;
- das **sichere Schliessen von QGIS**;
- das **erneute Oeffnen von QGIS** mit demselben geladenen Projekt;
- das **Warten einiger Sekunden** vor dem Neustart, damit Speicher und Buffer bereinigt werden koennen.

---

## Wann man es verwenden sollte

### Neustart, um QGIS zu "entfrieren"
Wenn die Anwendung langsam oder instabil reagiert, kann ein Neustart helfen:
- gibt angesammelten Cache-Speicher frei;
- setzt interne Plugin-Zustaende zurueck;
- bereinigt Rendering-Buffer.

### Nach der Installation eines neuen Plugins
Einige Plugins benoetigen einen Neustart, um korrekt zu funktionieren.

### Teilweise Wiederherstellung nach Haken
Wenn bestimmte Funktionen nicht reagieren, QGIS aber nicht vollstaendig eingefroren ist.

### Nicht verwenden fuer:
- das Speichern eines noch nie gespeicherten Projekts ohne Kontrolle;
- das Schliessen von Projekten, die Sie nicht erneut oeffnen wollen.

---

## Verwendung

### 1. Werkzeug oeffnen
Menue -> **Cadmus** -> **System** -> **Projekt speichern, schliessen und neu oeffnen**

---

### 2. Bestaetigen, falls noetig
Wenn das Projekt **noch nicht gespeichert** wurde:
- das Werkzeug fragt: `"Moechten Sie jetzt speichern?"`
- klicken Sie auf **Ja**, um vor dem Neustart zu speichern;
- waehlen Sie Speicherort und Namen der `.qgz`-Datei;
- klicken Sie auf **Speichern**.

---

### 3. Warten
Das Werkzeug wird:
1. das Projekt speichern, wenn Aenderungen vorhanden sind;
2. eine Meldung anzeigen: `"QGIS wird in wenigen Sekunden neu gestartet..."`;
3. QGIS nach etwa 2 Sekunden schliessen;
4. QGIS automatisch mit demselben Projekt neu oeffnen.

---

## Interne Funktionsweise

Das Werkzeug fuehrt diese Schritte aus:

1. **Validierung:** prueft, ob das Projekt auf der Festplatte gespeichert wurde
2. **Save:** fuehrt `project.write()` aus, um Aenderungen zu schreiben
3. **Skripterzeugung:** erzeugt die temporaere Datei `restart_qgis.bat` in `%TEMP%`
4. **Shell Execution:** fuehrt das Skript ueber `subprocess.Popen()` aus
5. **Shutdown:** verbindet einen Callback mit dem Qt-Signal `aboutToQuit`
6. **Restart:** das Skript wartet etwa 1 Sekunde und startet QGIS mit der `.qgz`-Datei

---

## Wichtige Hinweise

### Noch nicht gespeichertes Projekt
Wenn das Projekt noch nie auf die Festplatte gespeichert wurde:
- fordert das Werkzeug einen Speicherpfad an;
- der Benutzer waehlt Ordner und Dateinamen, zum Beispiel `mein_projekt.qgz`;
- das Projekt wird vor dem Neustart gespeichert.

### Aenderungen werden gespeichert
Alle Aenderungen seit dem letzten Speichern werden **vor dem Schliessen auf die Festplatte geschrieben**.

### Temporare Layer gehen verloren
Wenn Sie **Speicher-Layer** erstellt haben, die nicht als Datei gespeichert wurden:
- werden sie nach dem Neustart **nicht wiederhergestellt**;
- Workaround: Exportieren Sie diese Layer vor dem Neustart in eine Datei.

### Laufende Plugin-Dateien
Wenn ein Plugin gerade eine temporaere Datei erzeugt:
- kann diese waehrend des Neustarts verloren gehen;
- gut strukturierte Plugins speichern ihren Zustand in Einstellungen.

### Dauer des Neustarts
- **QGIS schliessen:** etwa 1 bis 2 Sekunden
- **QGIS neu oeffnen:** etwa 5 bis 15 Sekunden, je nach Projektgroesse
- **Gesamt:** etwa 6 bis 17 Sekunden

### QGIS-Executable
Das Werkzeug erkennt die verwendete QGIS-Executable automatisch:
- ueber `QCoreApplication.applicationFilePath()`;
- keine manuelle Konfiguration erforderlich.

---

## Interner Werkzeugschluessel

Dieses Werkzeug **speichert keine Einstellungen**. Es gibt keine Konfigurationsoptionen.

---

## Moegliche Probleme

### Problem: "QGIS oeffnet sich nicht erneut"
**Ursache:** Die QGIS-Executable wurde nicht gefunden.
**Loesung:**
- QGIS neu installieren;
- pruefen, ob QGIS im Standardpfad installiert wurde;
- das Werkzeug erneut ausfuehren.

### Problem: "Projekt wurde nicht gespeichert"
**Ursache:** Fehler beim Schreiben der `.qgz`-Datei.
**Loesung:**
- die **Ordnerberechtigungen** pruefen;
- den verfuegbaren **Festplattenspeicher** pruefen;
- sicherstellen, dass die `.qgz`-Datei nicht in einem anderen Programm geoeffnet ist.

### Problem: "Projekt ist nach dem Neustart leer"
**Ursache:** Das Projekt wurde gespeichert, aber nicht korrekt geladen.
**Loesung:**
- **Datei -> Zuletzt verwendet** oeffnen und das Projekt auswaehlen;
- oder **Datei -> Oeffnen** und manuell zur `.qgz`-Datei navigieren.

---

## Technische Informationen fuer Entwickler

- **Hauptfunktion:** `run_restart_qgis(iface)`
- **Executor:** `_RestartExecutor` fuer die Trennung der Verantwortlichkeiten
- **Logging:** strukturiert ueber `LogUtilsNew` mit semantischen Codes:
  - `RESTART_START` - Beginn des Ablaufs
  - `RESTART_SAVED` - Projekt erfolgreich gespeichert
  - `RESTART_SCRIPT_OK` - `.bat`-Skript erfolgreich erstellt
  - `RESTART_EXECUTING` - Neustartsequenz wird gestartet
  - `RESTART_CLOSING` - QGIS wird beendet
- **Temporaeres Skript:** gespeichert unter `%TEMP%/restart_qgis.bat`
- **Thread-Safety:** Skript wird ueber das Signal `aboutToQuit` im Main Thread ausgefuehrt

---

## Nutzungstipps

- Verwenden Sie das Werkzeug regelmaessig, wenn QGIS langsam wird.
- Speichern Sie Ihre Projekte haeufig mit `Ctrl+S`.
- Schliessen Sie unnoetige Projekte vor dem Neustart.
- Wenn der Neustart fehlschlaegt, koennen Sie die Wartezeit im Skript `restart_qgis.bat` anpassen.

---

## Fazit

Ein sicheres Werkzeug, um QGIS neu zu starten, ohne Projektarbeit zu verlieren. Es speichert immer vor dem Schliessen, und bereits gespeicherte Aenderungen bleiben erhalten.
