# -*- coding: utf-8 -*-
from .Strings_pt_BR import Strings_pt_BR


class Strings_de(Strings_pt_BR):
    """Strings for German (de-DE)"""

    # General
    APP_NAME = "Cadmus"
    PLUGIN_LANGUAGE = "Plugin-Sprache"

    # About
    ABOUT_CADMUS = "Über Cadmus"
    VERSION = "Version"
    UPDATED_ON = "Aktualisiert am"
    CREATED_ON = "Erstellt am"
    CREATOR = "Ersteller"
    LOCATION = "Speicherort"

    # Buttons
    CLOSE = "Schließen"
    SAVE = "Speichern"
    LOAD_FILES = "Dateien laden"
    EXPORT = "Exportieren"
    CANCEL = "Abbrechen"
    EXECUTE = "Ausführen"
    COPIED = "Kopiert"
    COPY = "Kopieren"
    SELECT = "Auswählen"
    REMOVE = "Entfernen"
    INVERT = "Umkehren"
    ENABLE = "Aktivieren"
    INFO = "Info"
    INSTRUCTIONS = "Anleitungen"
    AUTO_DETECT = "Automatisch erkennen"

    # Common labels
    PRECISION = "Genauigkeit"
    CONTINUE_ANYWAY = "Trotzdem fortfahren"
    MENU_SYSTEM = "System"
    MENU_LAYOUTS = "Layouts"
    MENU_FOLDER = "Ordner"
    MENU_VECTOR = "Vektor"
    MENU_AGRICULTURE = "Landwirtschaft"
    MENU_RASTER = "Raster"
    OPTIONS = "Optionen"
    SAVING = "Speichern"
    STYLES = "Stile"
    WARNING = "Warnung"
    ERROR = "Fehler"
    ADVANCED_PARAMETERS = "Erweiterte Parameter"
    APP_PREFERENCES = "Anwendungseinstellungen"
    OPEN_PREFERENCES_FOLDER = "Einstellungsordner öffnen"
    FILE_TYPES = "Dateitypen"
    ROOT_FOLDER = "Stammordner:"
    OUTPUT_FOLDER = "Ausgabeordner:"
    INPUT_LINE_LAYER = "Linienlayer (EINGABE):"
    SOURCE_LAYER = "Quelllayer:"
    TARGET_LAYER = "Ziellayer:"
    IMPLEMENT_SIZE = "Gerätegröße: (immer in Metern)"
    VECTOR_CALCULATION_METHOD = "Vektorberechnungsmethode"
    VECTOR_FIELDS_PRECISION = "Genauigkeit der Vektorfelder (Dezimalstellen):"
    ASYNC_THRESHOLD = "Asynchronschwellenwert (Anzahl Objekte):"
    CALCULATION_METHOD_LABEL = "Vektorberechnungsmethode:"
    SEARCH_TEXT = "Suchtext:"
    REPLACE_WITH_NEW_TEXT = "Ersatztext (neu):"
    SOURCE_LAYER_ATTRIBUTES = "Attribute des Quelllayers"
    ATTRIBUTES = "Attribute"
    USE_ALL_ATTRIBUTES = "Alle Attribute verwenden"
    EXPORT_OPTIONS = "Exportoptionen"
    MAX_WIDTH_PNG = "Max. Breite für PNG (px):"
    USE_PROJECT_FOLDER = "Projektordner verwenden"
    EXPORT_PDF = "PDF exportieren"
    EXPORT_PNG = "PNG exportieren"
    MERGE_PDFS_FINAL = "PDFs zu einer finalen PDF zusammenführen"
    MERGE_PNGS_FINAL = "PNGs zu einer finalen PDF zusammenführen"
    REPLACE_EXISTING_FILES = "Vorhandene Dateien ersetzen"
    WGS84_EPSG4326 = "WGS 84 (EPSG:4326)"
    UTM_SIRGAS_2000 = "UTM SIRGAS 2000"
    ALTIMETRY_OPENTOPO = "Höhenmessung (OpenTopoData)"
    APPROX_ALTITUDE_METERS = "Ungefähre Höhe (m)"
    LATITUDE_DECIMAL = "Breitengrad (Dezimal)"
    LONGITUDE_DECIMAL = "Längengrad (Dezimal)"
    LATITUDE_DMS = "Breitengrad (DMS)"
    LONGITUDE_DMS = "Längengrad (DMS)"
    EASTING_X = "Rechtswert (X)"
    NORTHING_Y = "Hochwert (Y)"
    ADDRESS_OSM = "Adresse (OSM):"
    COPY_WGS84_FULL = "WGS 84 kopieren (vollständig)"
    COPY_UTM_FULL = "UTM kopieren (vollständig)"
    COPY_LOCATION_FULL = "Standort kopieren (vollständig)"
    POINT_COORDINATES = "Punktkoordinaten"
    ZONE = "Zone"
    HEMISPHERE = "Hemisphäre"
    CITY = "Gemeinde"
    FILE_NOT_FOUND = "Datei nicht gefunden"
    INTERMEDIATE_REGION = "Zwischenregion"
    STATE = "Bundesland"
    REGION = "Region"
    COUNTRY = "Land"
    LOADING = "Wird geladen..."
    LOADING_LOWER = "wird geladen..."
    UNAVAILABLE = "Nicht verfügbar"
    NO_PATH_SELECTED = "Kein Pfad ausgewählt"
    FILES_SELECTED = "Datei(en) ausgewählt"
    ITEMS_SELECTED = "Element(e)"
    ONLY_SELECTED_FEATURES = "Nur ausgewählte Objekte"
    APPLY_QML_STYLE = "QML-Stil anwenden"
    QML_LABEL = "QML:"
    SAVE_TO_FILE = "In Datei speichern:"
    SELECT_PATH = "Pfad auswählen"
    BUTTON = "Schaltfläche"
    SAVE_FILE = "Datei speichern"
    SELECT_FILE = "Datei auswählen"
    POINTS = "Punkte"
    TRACK = "Spur"

    # Common option labels
    CASE_SENSITIVE = "Groß-/Kleinschreibung beachten"
    FULL_LABEL_REPLACE = "Gesamten Label-Inhalt ersetzen, wenn Text gefunden wird"
    LOAD_ONLY_MISSING_FILES = (
        "Nur Dateien laden, die noch NICHT im Projekt geladen sind"
    )
    PRESERVE_FOLDER_STRUCTURE = (
        "Gruppen entsprechend der Ordner-/Unterordnerstruktur erstellen"
    )
    DO_NOT_GROUP_LAST_FOLDER = "Letzten Ordner nicht gruppieren"
    CREATE_PROJECT_BACKUP_IF_SAVED = (
        "Projektsicherung erstellen, bevor geladen wird (nur wenn gespeichert)"
    )

    # Common messages
    SUCCESS_MESSAGE = "Verarbeitung erfolgreich abgeschlossen."
    ERROR_LAYER_NOT_FOUND = "Fehler: Layer nicht gefunden."
    SELECT_VALID_FOLDER = "Bitte einen gültigen Ordner auswählen."
    SELECT_AT_LEAST_ONE_FILE_TYPE = "Bitte mindestens einen Dateityp auswählen."
    SELECT_AT_LEAST_ONE_EXPORT_FORMAT = (
        "Bitte mindestens ein Format auswählen (PDF oder PNG)"
    )
    SELECT_VALID_LINE_LAYER = "Bitte einen gültigen Linienlayer auswählen."
    INVALID_SOURCE_LAYER = "Ungültiger Quelllayer"
    INVALID_TARGET_LAYER = "Ungültiger Ziellayer"
    INVALID_INPUT_LAYER = "Ungültiger Eingabelayer."
    FINAL_LAYER_NOT_FOUND = "Fehler: Finaler Layer im Kontext nicht gefunden."
    BUFFER_CANNOT_BE_ZERO = "Puffer darf nicht 0 sein"
    ASYNC_STARTED = (
        "Hintergrundausführung gestartet. Fortschritt im Protokoll verfolgen."
    )
    ASYNC_START_ERROR = "Fehler beim Starten der asynchronen Ausführung:"
    ASYNC_FINISHED = "Asynchrone Ausführung abgeschlossen."
    ASYNC_EXECUTION_ERROR = "Fehler bei der asynchronen Ausführung:"
    FILES_LOADED_PREFIX = "Es wurden geladen"
    FILES_SUFFIX = "Dateien."
    SETTINGS_SAVED_TITLE = "Einstellungen gespeichert"
    SETTINGS_SAVED_MESSAGE = "Die Einstellungen wurden erfolgreich gespeichert."
    PREFERENCES_FOLDER_NOT_FOUND = "Einstellungsordner nicht gefunden:"
    ENTER_TEXT_TO_SEARCH = "Bitte Suchtext eingeben."
    CONFIRM_REPLACEMENTS = "Ersetzungen bestätigen"
    SEARCH_LABEL = "Suchen:"
    REPLACE_WITH_LABEL = "Ersetzen durch:"
    DESTRUCTIVE_OPERATION_WARNING = "Achtung – destruktive Operation"
    LAYOUTS_ANALYZED = "Analysierte Layouts:"
    CHANGES_APPLIED = "Angewandte Ersetzungen:"
    REPLACEMENT_COMPLETED_TITLE = "Ersetzung abgeschlossen"
    PROJECT_BACKUP_INFO = "Sicherung: Es wird eine Kopie des Projekts (.qgz) im Ordner 'backup' neben der Projektdatei erstellt."
    LAYER_MUST_BE_EDITABLE = "Der Layer muss sich im Bearbeitungsmodus befinden"
    NO_ATTRIBUTE_SELECTED = "Kein Attribut ausgewählt"
    ATTRIBUTES_COPIED_SUCCESS = (
        "Attribute erfolgreich kopiert (Änderungen nicht gespeichert)"
    )
    REQUIRED_LIBRARY = "Erforderliche Bibliothek"
    PYPDF2_REQUIRED_MESSAGE = "Zum Zusammenführen von PDFs muss das Paket PyPDF2 installiert werden.\n\nJetzt installieren?"
    PILLOW_REQUIRED_MESSAGE = "Zum Zusammenführen von PNGs zu PDF muss das Paket Pillow installiert werden.\n\nJetzt installieren?"
    EXPORTING_LAYOUTS = "Layouts werden exportiert..."
    FAILED_EXPORT_PDF = "PDF-Export fehlgeschlagen:"
    FAILED_EXPORT_PNG = "PNG-Export fehlgeschlagen:"
    ERROR_EXPORTING = "Fehler beim Exportieren"
    FAILED_MERGE_PDFS = "PDF-Zusammenführung fehlgeschlagen:"
    FAILED_MERGE_PNGS = "PNG-Zusammenführung fehlgeschlagen:"
    ERRORS_FOUND = "Gefundene Fehler:"
    LAYOUTS_EXPORTED_SUCCESS = "Layout(s) erfolgreich exportiert!"
    PDFS_MERGED = "PDFs zusammengeführt"
    PNGS_MERGED = "PNGs zusammengeführt"
    EXPORT_LAYOUTS_COMPLETED = "Layout-Export abgeschlossen"
    LOCATION_COPIED_TO_CLIPBOARD = "Standort in die Zwischenablage kopiert"
    ADDRESS_COPIED_TO_CLIPBOARD = "Adresse in die Zwischenablage kopiert"

    SELECT_VECTOR_LAYER = "Bitte einen Vektorlayer auswählen"
    SELECT_EDITABLE_VECTOR_LAYER = "Bitte einen bearbeitbaren Vektorlayer auswählen"
    LAYER_HAS_NO_FEATURES = "Der Layer enthält keine Objekte"
    OPERATION_CANCELLED_BY_USER = "Vorgang vom Benutzer abgebrochen"
    GEOMETRY_TYPE_NOT_SUPPORTED = "Geometrietyp wird nicht unterstützt"
    ERROR_IN_PREPARATION = "Fehler bei der Vorbereitung:"
    KML_FILES_ARE_NOT_EDITABLE = "KML-Dateien sind nicht bearbeitbar."
    CONVERT_LAYER_TO_GPKG_OR_SHP_BEFORE_USING = "Bitte den Layer vor der Verwendung dieses Werkzeugs in GeoPackage (.gpkg) oder Shapefile (.shp) konvertieren."
    LAYER_USES_GEOGRAPHIC_CRS = "Layer verwendet ein geografisches KBS"
    CARTESIAN_MODE_RESULTS_IN_DEGREES2 = (
        "Der Modus 'Kartesisch' würde Werte in Grad² liefern."
    )
    CALCULATING_BOTH_MODES_AUTOMATICALLY = "Beide Modi werden automatisch berechnet."
    XY_FIELDS_CALCULATED_SUCCESS = "X/Y-Felder erfolgreich berechnet"
    LINE_LENGTH_CALCULATED_SUCCESS = "Linienlänge erfolgreich berechnet"
    POLYGON_AREA_CALCULATED_SUCCESS = "Polygonfläche erfolgreich berechnet"
    ERROR_STARTING_CALCULATION = "Fehler beim Starten der Berechnung:"
    UNKNOWN_ERROR = "Unbekannter Fehler"
    CALCULATION_FAILED = "Berechnung fehlgeschlagen:"
    GEOMETRIES_CONVERTED_TO_MULTIPART_NOT_SAVED = (
        "Geometrien in Multipart umgewandelt (nicht gespeichert)"
    )
    CONVERT_SELECTED_FEATURES_TO_MULTIPART = (
        "Nur die ausgewählten Objekte in Multipart umwandeln?"
    )
    CONVERT_ALL_FEATURES_TO_MULTIPART = "Alle Objekte in Multipart umwandeln?"

    # Dependencies
    INSTALLING_DEPENDENCY = "Abhängigkeit wird installiert..."
    INSTALLING_DEPENDENCIES = "Abhängigkeiten werden installiert"
    DEPENDENCY = "Abhängigkeit"
    INSTALLED_SUCCESSFULLY = "erfolgreich installiert."
    SUCCESS = "Erfolg"
    INSTALL_DEPENDENCY_FAILED = (
        "Installation der Bibliothek konnte nicht gestartet werden."
    )
    KML_FIELDS_REMOVED_SUCCESS = "KML-Felder erfolgreich entfernt"
    NO_KML_FIELDS_FOUND = "Keine KML-Felder zum Entfernen gefunden"
    ERROR_REMOVING_KML_FIELDS = "Fehler beim Entfernen der KML-Felder:"
    RANGE = "Bereich"
    RASTERS = "Raster"
    INPUT_POINTS = "Eingabepunkte"
    REPROJECT_OUTPUT_LAYER_OPTIONAL = "Ausgabelayer umprojizieren (optional)"
    SAMPLED_VALUES = "Beprobte_Werte"
    OPEN_OUTPUT_FOLDER = "Ausgabeordner öffnen"
    DISPLAY_HELP_FIELD = "Hilfefeld anzeigen (Ausführung und Neustart erforderlich)"
    OUTPUT_CRS_LABEL = "Ausgabe-KBS:"
    NONE = "Keine"
    FILE_SAVED_IN = "Datei gespeichert in:"
    RASTER_MASS_SAMPLER_TITLE = "Massen-Rasterbeprobung"
    RASTER_WEIGHTED_AVERAGE_TITLE = "Gewichteter Durchschnitt von Rastern"
    RASTER_MASS_CLIPPER_TITLE = "Massenzuschnitt von Rastern"
    RASTER_MASS_SAMPLER_TOOLTIP = (
        "Führt eine Stapel-Beprobung mehrerer Raster über einem Vektorlayer aus.\n"
        "Öffnet den Cadmus-Provider-Algorithmus im Processing,\n"
        "sodass Eingaben, Felder und Ausgaben in der Standardoberfläche konfiguriert werden können."
    )
    RASTER_MASS_CLIPPER_TOOLTIP = (
        "Schneidet mehrere Raster stapelweise mit einem Polygonlayer als Maske zu.\n"
        "Öffnet den Cadmus-Provider-Algorithmus im Processing,\n"
        "mit Unterstützung für Zuschnitt pro Feature, Korrekturpuffer und Ausgabeordner."
    )
    RASTER_DIFFERENCE_STATISTICS_TITLE = "Rasterdifferenz verarbeiten"
    VECTOR_TO_SVG_TITLE = "Vektor-zu-SVG-Konverter"
    VECTOR_TO_SVG_TOOLTIP = (
        "Exportiert einen Vektorlayer des Projekts nach SVG.\n"
        "Erlaubt die Konfiguration von Hintergrund, Rand und Beschriftung\n"
        "und kann entweder eine einzelne Datei oder ein separates SVG\n"
        "pro Feature erzeugen."
    )
    VECTOR_LAYER_LABEL = "Vektorlayer"
    BACKGROUND_COLOR = "Hintergrundfarbe"
    BORDER_COLOR = "Randfarbe"
    BORDER_WIDTH = "Randstärke"
    LABEL_COLOR = "Beschriftungsfarbe"
    LABEL_SIZE = "Beschriftungsgröße"
    SELECT_FILL_COLOR = "Füllfarbe auswählen"
    SELECT_BORDER_COLOR = "Randfarbe auswählen"
    SELECT_LABEL_COLOR = "Beschriftungsfarbe auswählen"
    TRANSPARENT_BACKGROUND = "Transparenter Hintergrund"
    SHOW_BORDER = "Rand anzeigen"
    SHOW_LABEL = "Beschriftung anzeigen"
    GENERATE_SVG_FOR_EACH_FEATURE = "SVG für jedes Feature erzeugen"
    SVGS_GENERATED_SUCCESS = "SVG(s) erfolgreich erzeugt."
    INPUT_MASK_POLYGON_LAYER = "Maskenlayer (Polygon)"
    CLIP_PER_EACH_POLYGON = "Pro Polygon zuschneiden"
    APPLY_CORRECTION_BUFFER_PIXEL_1_1 = "Korrekturpuffer anwenden (Pixel * 1,1)"
    RASTER_FOLDER_OR_SELECT_RASTER_LAYERS = "Rasterordner oder Rasterlayer auswählen"
    QGIS_RASTER_LAYERS_OR_SELECT_RASTER_FOLDER = (
        "QGIS-Rasterlayer oder Rasterordner auswählen"
    )
    OUTPUT_FOLDER_FOR_GENERATED_RASTERS = "Ausgabeordner für erzeugte Raster"
    NO_OUTPUT_FOLDER_PROVIDED_USING_TEMP = (
        "Kein Ausgabeordner angegeben. Temporären Ordner wird verwendet:"
    )
    INVALID_FOLDER = "Ungültiger Ordner"
    NO_RASTER_FOUND_IN_SPECIFIED_FOLDER = "Kein Raster im angegebenen Ordner gefunden."
    INVALID_RASTER_IGNORED = "Ungültiges Raster übersprungen"
    PROCESSING_RASTER_DIFFERENCE_BY_FOLDER_OR_LAYERS = (
        "Rasterdifferenz nach Ordner/Layern wird verarbeitet..."
    )
    INFORM_RASTER_FOLDER_OR_SELECT_LAYER = (
        "Bitte einen Rasterordner angeben oder mindestens einen Rasterlayer auswählen."
    )
    AT_LEAST_2_RASTERS_REQUIRED = (
        "Mindestens 2 Raster sind erforderlich, um Differenzen zu berechnen."
    )
    FOUND_RASTER_COMBINATIONS_FOR_DIFFERENCE = (
        "Gefundene Rasterkombinationen für die Differenzierung:"
    )
    PROCESSING = "Wird verarbeitet"
    NO_OVERLAP_BETWEEN = "Keine Überschneidung zwischen"
    AND = "und"
    SKIPPING = "Wird übersprungen"
    CALCULATION_ERROR_FOR = "Berechnungsfehler für"
    DIFFERENCE_RASTER_CREATED = "Differenzraster erstellt:"
    STATS_GENERATED_FOR = "Statistiken generiert für"
    FAILED_TO_GENERATE_STATS_FOR = "Fehler beim Generieren der Statistiken für"
    CONSOLIDATED_REPORT_GENERATED = "Konsolidierter Bericht erstellt:"
    DIFFERENCE_STATISTICS_SUMMARY_TITLE = (
        "Zusammenfassung der Rasterdifferenz-Statistiken"
    )
    TOTAL_PROCESSED_PAIRS = "Gesamt verarbeitete Paare:"
    RASTER = "Raster"
    STATISTICS = "Statistiken"
    VECTOR = "Vektor"
    INTERVAL = "Intervall"
    GEOMETRY_LINE_FROM_POINTS_TITLE = "Differenzlinie zwischen Punkten"
    POINT_LAYER_MODE1_FIRST_LAYER_MODE2 = (
        "Punktlayer (Modus 1) / Erster Layer (Modus 2)"
    )
    BASE_ATTRIBUTE_LAYER_A = "Basisattribut – Layer A"
    USE_SECOND_LAYER_MODE2 = "Zweiten Layer verwenden (Modus 2)"
    SECOND_POINT_LAYER_MODE2_OPTIONAL = "Zweiter Punktlayer (Modus 2 – optional)"
    BASE_ATTRIBUTE_LAYER_B_MODE2 = "Basisattribut – Layer B (Modus 2)"
    DIFFERENCE_LINES = "Differenzlinien"
    INVALID_LAYER_A = "Layer A ungültig."
    MODE2_REQUIRES_SECOND_POINT_LAYER = "Modus 2 erfordert einen zweiten Punktlayer."
    MODE2_INFORM_GROUP_FIELD_LAYER_B = (
        "Im Modus 2 bitte das Gruppierungsfeld für Layer B angeben."
    )
    ERROR_CREATING_OUTPUT_LAYER = "Fehler beim Erstellen des Ausgabelayers."
    PROCESS_COMPLETED_LINES_GENERATED_SUCCESS = (
        "Vorgang abgeschlossen: Linien erfolgreich generiert."
    )
    GRID_GENERATOR_TITLE = "Grid-Generator"
    GRID_GENERATOR_INPUT_LAYER = "Eingabelayer (Polygon)"
    HORIZONTAL_SPACING = "Horizontaler Abstand"
    VERTICAL_SPACING = "Vertikaler Abstand"
    GRID_TYPE = "Gittertyp"
    OUTPUT_GRID = "Ausgabegitter"
    VERBOSE_LOG = "Detailliertes Protokoll"
    ATTRIBUTE_STATISTICS_TITLE = "Attributstatistiken"
    INPUT_LAYER = "Eingabelayer"
    EXCLUDE_FIELDS_OPTIONAL = "Felder ausschließen (optional)"
    PRECISION_DECIMAL_PLACES = "Genauigkeit (Dezimalstellen)"
    LOAD_CSV_AUTOMATICALLY_AFTER_EXECUTION = "CSV nach der Ausführung automatisch laden"
    FORCE_CSV_PTBR_FORMAT = (
        "CSV im PT-BR-Format erzwingen (Semikolon und Komma verwenden)"
    )
    CALCULATE = "Berechnen"
    OUTPUT_CSV_FILE = "CSV-Ausgabedatei"
    INVALID_LAYER = "Ungültiger Layer."
    NO_NUMERIC_FIELD_FOUND = "Kein numerisches Feld gefunden."
    FIELD = "Feld"
    COUNT = "Anzahl"
    ERROR_SAVING_CSV = "Fehler beim Speichern der CSV:"
    FILE_LOADED_AS_LAYER = "Datei als Layer geladen:"
    CSV_FILE_GENERATED = "CSV-Datei erstellt:"
    MEAN = "Mittelwert"
    MEAN_ABSOLUTE = "Absoluter Mittelwert"
    STD_POP = "Standardabweichung (Grundgesamtheit)"
    STD_SAMPLE = "Standardabweichung (Stichprobe)"
    MINIMUM = "Minimum"
    MAXIMUM = "Maximum"
    MEDIAN = "Median"
    PERCENTILE_5 = "Perzentil 5%"
    PERCENTILE_95 = "Perzentil 95%"
    MODE = "Modalwert"
    VARIANCE = "Varianz"
    SUM = "Summe"
    COEFFICIENT_OF_VARIATION = "Variationskoeffizient"
    SKEWNESS = "Schiefe"
    KURTOSIS = "Kurtosis"
    DIFFERENCE_FIELDS_TITLE = "Felddifferenz-Generator"
    POINT_LAYER = "Punktlayer"
    BASE_FIELD_SUBTRAHEND = "Basisfeld (Subtrahend)"
    FIELDS_TO_EXCLUDE_FROM_CALCULATION = "Felder von der Berechnung AUSSCHLIESSEN"
    PREFIX_FOR_NEW_FIELDS = "Präfix für neue Felder"
    DIFFERENCE = "Differenz"
    NO_EXCLUDED_FIELD_USING_ALL_NUMERIC = (
        "Kein Feld ausgeschlossen → alle numerischen Felder werden verwendet."
    )
    BASE = "Basis"
    EXCLUDED_FIELDS = "AUSGESCHLOSSENE Felder"
    FIELDS_USED_IN_CALCULATION = "In der Berechnung verwendete Felder"
    PREFIX = "Präfix"
    PROCESS_FINISHED_SUCCESS = "Vorgang erfolgreich abgeschlossen."

    # plugins/DroneCoordinates.py
    DRONE_COORDINATES_TITLE = "DJI Drohnenkoordinaten"
    DRONE_COORDINATES_TOOLTIP = (
        "Liest MRK-Dateien von Drohnen, um Fotostandorte und den Flugpfad zu erzeugen.\n"
        "Kann die Punkte mit Bildmetadaten verknüpfen,\n"
        "Ergebnisse in eine Datei speichern und QML-Stile\n"
        "auf die erzeugten Punkte und den Pfad anwenden."
    )
    RECURSIVE_SEARCH = "Unterordner durchsuchen"
    USE_MRK_DATA = "MRK-Daten abrufen"
    PHOTOS_METADATA = "Mit Fotometadaten verknüpfen"
    PHOTOS_METADATA_REQUIRED_MESSAGE = "Zum Verknüpfen mit Fotometadaten muss das Paket Pillow installiert werden.\n\nJetzt installieren?"
    GENERATE_REPORT = "Bericht generieren"
    MRK_FOLDER = "MRK-Ordner:"
    SAVE_POINTS_CHECKBOX = "MRK-Punkte in Datei speichern?"
    SAVE_IN = "Speichern in:"
    SAVE_TRACK_CHECKBOX = "Spur in Datei speichern?"
    USE_LOGO = "Logo verwenden?"
    LOGO_LABEL = "Logo:"
    PROJECT_TITLE = "Projekttitel"
    PROJECT_TITLE_HINT = "Z.B.: Hoffnungshof"
    APPLY_STYLE_POINTS = "Stil (QML) auf Punkte anwenden?"
    QML_POINTS = "QML Punkte:"
    APPLY_STYLE_TRACK = "Stil (QML) auf Spur anwenden?"
    QML_TRACK = "QML:"
    MRK_DROP_START = "MRK-Datei erkannt. Konvertierung wird gestartet."
    CONVERT_FILE_SUCCESS = "Datei erfolgreich konvertiert."
    LOADED_EXISTING_GPKG = "Vorhandene GPKG-Ausgaben erfolgreich geladen."
    CONVERT_FILE_ERROR = "Dateikonvertierung fehlgeschlagen."
    REPORT_METADATA_TITLE = "Metadatenbericht"
    REPORT_METADATA_TOOLTIP = (
        "Listet temporäre Metadaten-JSON-Dateien und erzeugt den HTML-Bericht erneut.\n"
        "Bietet zudem einen Schnellzugriff auf den Berichtsordner."
    )
    REFRESH_JSON_LIST = "JSON-Liste aktualisieren"
    OPEN_REPORTS_FOLDER = "Berichtsordner öffnen"
    OPEN_JSONS_FOLDER = "JSON-Ordner öffnen"
    VECTOR_WITHOUT_MRK_BLOCK_TITLE = "Vektor Ohne MRK Erzeugen"
    VETORIZE_FLIGHT = "Flug vektorisieren"
    VETORIZE_FLIGHT_TOOLTIP = (
        "Erzeugt Punkt- und Spur-Vektorebenen aus dem ausgewählten Metadaten-JSON.\n"
        "Entspricht der Ausführung der Drohnenkoordinaten-Pipeline nur mit dem JSON."
    )
    NO_JSON_FOUND = "Keine temporären JSON-Dateien gefunden."

    # plugins/SettingsPlugin.py
    SETTINGS_TITLE = "Cadmus-Einstellungen"
    SETTINGS_TOOLTIP = (
        "Öffnet die globalen Cadmus-Einstellungen.\n"
        "Ermöglicht das Festlegen der Standard-Vektorberechnungsmethode,\n"
        "der Genauigkeit der Vektorfelder und des Objekt-Schwellenwerts\n"
        "für die asynchrone Verarbeitung."
    )
    GENERAL = "Allgemein"
    DEFAULT_CRS = "Standard-KBS"
    PROJECTS_FOLDER = "Projektordner"
    TOOLBAR_VISIBLE_CATEGORIES = "Werkzeugleiste – Sichtbare Kategorien"
    VECTOR_CALCULATIONS_PLUGIN = "Plugin für Vektorberechnungen"
    CARTESIAN_SUFFIX = "Kartesisches Suffix"
    ELLIPSOIDAL_SUFFIX = "Ellipsoidisches Suffix"
    AREA_SUFFIXES_CANNOT_MATCH = (
        "Kartesisches und ellipsoidisches Suffix dürfen nicht identisch sein."
    )
    ELLIPSOIDAL = "Ellipsoidisch"
    CARTESIAN = "Kartesisch"
    BOTH = "Beides"

    # plugins/ReplaceInLayouts.py
    REPLACE_IN_LAYOUTS_TITLE = "Text in Layouts ersetzen"
    REPLACE_IN_LAYOUTS_TOOLTIP = (
        "Sucht Texte in den Beschriftungen der Projekt-Layouts\n"
        "und ersetzt sie durch den angegebenen neuen Wert.\n"
        "Ermöglicht teilweisen Ersatz oder vollständigen Austausch\n"
        "des Beschriftungsinhalts bei Übereinstimmung."
    )
    REPLACE_IN_LAYOUTS_SWAP = "Tauschen"
    REPLACE_IN_LAYOUTS_RUN = "Ersetzung ausführen"

    # plugins/LoadFolderLayers.py
    LOAD_FOLDER_LAYERS_TITLE = "Ordner mit Dateien laden"
    CREATE_PROJECT_TITLE = "Neues Projekt"
    CREATE_PROJECT_TOOLTIP = (
        "Erstellt eine neue Projektstruktur in einem dedizierten Ordner.\n"
        "Falls noch kein Standardordner festgelegt ist, wird dieser Pfad abgefragt,\n"
        "dann der Projektordner, die .qgz-Datei\n"
        "und die Unterordner vectors und rasters erstellt."
    )
    DEFAULT_PROJECTS_FOLDER_TITLE = "Standard-Projektordner"
    DEFAULT_PROJECTS_FOLDER_PROMPT = "Legen Sie den Standardordner fest, in dem neue Cadmus-Projekte erstellt werden."
    PROJECT_NAME_TITLE = "Neues Projekt"
    PROJECT_NAME_PROMPT = "Geben Sie den Projektnamen ein. Bei Leerlasse wird der vorgeschlagene Name verwendet."
    PROJECT_NAME_LABEL = "Projektname"
    PROJECTS_DEFAULT_FOLDER_MISSING = (
        "Es wurde kein Standardordner für Projekte festgelegt.\n\n"
        "Möchten Sie jetzt einen Standardordner festlegen?"
    )
    PROJECTS_DEFAULT_FOLDER_MISSING_TITLE = "Standardordner nicht festgelegt"
    PROJECT_FOLDER_ALREADY_EXISTS = "Der Projektordner existiert bereits:"
    PROJECT_FOLDER_CREATE_ERROR = "Die Projektstruktur konnte nicht erstellt werden:"
    PROJECT_FILE_CREATE_ERROR = "Das QGIS-Projekt konnte nicht erstellt werden:"
    PROJECT_DEFAULT_FOLDER_PREPARE_ERROR = (
        "Der Standardordner konnte nicht vorbereitet werden:"
    )
    PROJECT_DEFAULT_FOLDER_ACCESS_ERROR = (
        "Auf den Standardordner konnte nicht zugegriffen werden:"
    )
    CURRENT_PROJECT_SAVE_TO_NEW_DESTINATION_ERROR = (
        "QGIS konnte das aktuelle Projekt nicht am neuen Speicherort speichern."
    )
    NEW_PROJECT_FILE_WRITE_ERROR = "QGIS konnte die neue .qgz-Datei nicht schreiben."
    OPEN_NEW_QGIS_WINDOW_ERROR = "Das Projekt wurde erstellt, aber es konnte kein neues QGIS-Fenster geöffnet werden."
    PROJECT_CREATED_TITLE = "Projekt erstellt"
    PROJECT_CREATED_SUCCESS = "Projekt '{project_name}' erfolgreich erstellt"
    PROJECT_CREATED_OPENED_NEW_WINDOW = (
        "Projekt '{project_name}' erstellt und in einem neuen Fenster geöffnet"
    )
    LOAD_FOLDER_LAYERS_TOOLTIP = (
        "Lädt Vektor- und Rasterdateien stapelweise aus einem Ordner\n"
        "und seinen Unterordnern in das QGIS-Projekt.\n"
        "Kann nach Dateityp filtern, Duplikate vermeiden\n"
        "und Layer entsprechend der Ordnerstruktur organisieren."
    )

    # plugins/GenerateTrailPlugin.py
    GENERATE_TRAIL_TITLE = "Maschinenspur erzeugen"
    GENERATE_TRAIL_TOOLTIP = (
        "Erzeugt den von einem Gerät belegten Streifen aus einem Linienlayer.\n"
        "Konvertiert die angegebene Breite in die Einheit des Layers,\n"
        "wendet einen Puffer mit der Hälfte dieses Werts an und erstellt\n"
        "einen neuen Layer mit der resultierenden Spur."
    )

    # plugins/CopyAttributesPlugin.py
    COPY_ATTRIBUTES_TITLE = "Vektorattribute kopieren"
    COPY_ATTRIBUTES_TOOLTIP = (
        "Kopiert die Feldstruktur eines Quell-Vektorlayers\n"
        "in einen Ziel-Vektorlayer.\n"
        "Ermöglicht die Auswahl der zu erstellenden Attribute und\n"
        "die Behandlung von Namenskonflikten bei bereits vorhandenen Feldern."
    )

    # plugins/ExportAllLayouts.py
    EXPORT_ALL_LAYOUTS_TITLE = "Alle Layouts exportieren"
    EXPORT_ALL_LAYOUTS_TOOLTIP = (
        "Exportiert alle Projekt-Layouts als PDF, PNG oder beides.\n"
        "Kann die erzeugten PDFs in einer Enddatei zusammenführen,\n"
        "PNGs in PDF konvertieren und das Überschreiben\n"
        "von Dateien im Ausgabeordner steuern."
    )

    # plugins/VectorMultipartPlugin.py
    CONVERTER_MULTIPART_TITLE = "Multipart konvertieren"
    CONVERTER_MULTIPART_TOOLTIP = (
        "Verarbeitet Multipart-Objekte des aktiven Vektorlayers\n"
        "und trennt jeden Teil in ein eigenständiges Objekt.\n"
        "Kann nur auf ausgewählte Objekte oder auf den gesamten Layer\n"
        "angewendet werden, wobei die Attribute erhalten bleiben."
    )

    # plugins/CoordClickTool.py
    COORD_CLICK_TOOL_TITLE = "Koordinaten erfassen"
    COORD_CLICK_TOOL_TOOLTIP = (
        "Ermöglicht das Klicken auf die Karte, um Punktkoordinaten abzufragen.\n"
        "Öffnet einen Dialog mit WGS84, UTM, ungefährer Höhe\n"
        "und geschätzter Adresse sowie Optionen zum Kopieren\n"
        "in die Zwischenablage."
    )

    # core/ToolRegistry.py
    RESTART_QGIS_TITLE = "Projekt speichern, schließen und neu öffnen"
    RESTART_QGIS_TOOLTIP = (
        "Speichert das aktuelle Projekt, schließt QGIS und öffnet dasselbe Projekt erneut.\n"
        "Nützlich, um die Sitzung nach Abstürzen\n"
        "oder visuellen Problemen ohne Datenverlust wiederherzustellen."
    )
    LOGCAT_TITLE = "Logcat-Viewer"
    LOGCAT_TOOLTIP = (
        "Öffnet den Protokoll-Viewer des Plugins.\n"
        "Ermöglicht die Inspektion von Meldungen, Fehlern und internen Ereignissen,\n"
        "die von Cadmus aufgezeichnet wurden."
    )
    ABOUT_DIALOG_TOOLTIP = (
        f"Öffnet das Fenster '{ABOUT_CADMUS}' von {APP_NAME}.\n"
        "Zeigt allgemeine Informationen über das Plugin,\n"
        "wie Version, Autorenschaft und Projektkontext."
    )
    LAYER_NOT_EDITABLE_ASK = "Der Layer '{layer_name}' befindet sich nicht im Bearbeitungsmodus.\n\nMöchten Sie die Bearbeitung jetzt aktivieren?"
    LAYER_NOW_EDITABLE = "Layer wurde automatisch in den Bearbeitungsmodus versetzt."
    VECTOR_FIELDS_TITLE = "Vektorfelder berechnen"
    VECTOR_FIELDS_TOOLTIP = (
        "Berechnet automatisch Vektorfelder wie Fläche,\n"
        "Länge oder X/Y-Koordinaten im aktiven Layer.\n"
        "Nützlich, um technische Attribute zu erzeugen, ohne jedes Feld einzeln bearbeiten zu müssen."
    )
    REMOVE_KML_FIELDS_TITLE = "KML-Felder entfernen"
    REMOVE_KML_FIELDS_TOOLTIP = (
        "Entfernt typische KML-Attributfelder aus dem aktiven Layer.\n"
        "Das Werkzeug läuft nur, wenn der Layer bereits im Bearbeitungsmodus ist,\n"
        "und speichert nicht und beendet den Bearbeitungsmodus nicht."
    )

    # plugins/PathExtensionPlugin.py
    PATH = "Pfad"
    PATH_EXTENSION_TITLE = "Erweiterung Entfernen/Wiederherstellen"
    PATH_EXTENSION_TOOLTIP = "Entfernt oder stellt die Dateierweiterung in den Pfaden der Features wieder her"
    MODE_REMOVE = "Erweiterung entfernen"
    MODE_RESTORE = "Erweiterung wiederherstellen"
    MODE_ZIP = "Dateien komprimieren"
    MODE_UNZIP = "Dateien dekomprimieren"

    # Registry
    REG_TITLE = "Verwalten"
    REGISTRY_SAVED_SUCCESS = "Gespeichert und validiert."
    REGISTRY_DELETED_SUCCESS = "Erfolgreich entfernt."
    REGISTRY_INVALID = "Ungültig."
    REGISTRY_EMPTY = "Feld ausfüllen."
    NO_KEY = "kein Schlüssel"
    EXPIRATION_DATE = "Gültigkeit"
    REMAINING_DAYS = "verbleibende Tage"
    STATUS = "Status"
    LEVEL = "Stufe"
    ACTIVE = "Aktiv"
    INACTIVE = "Inaktiv"
    VALIDATE = "Validieren"

    # plugins/SaveTemporaryLayersPlugin.py
    SAVE_TEMPORARY_LAYER_TITLE = "Temporäre speichern"
    SAVE_TEMPORARY_LAYER_TOOLTIP = "Speichert temporäre (Memory-)Layer des Projekts als dauerhafte Dateien auf der Festplatte"
    EXTENSION_VECTOR = "Vektor-Erweiterung"
    EXTENSION_RASTER = "Raster-Erweiterung"
    VECTORS_FOLDER = "Vektorordner"
    RASTERS_FOLDER = "Rasterordner"
    SEPARATOR = "Trennzeichen"
    VECTOR_EXTENSIONS = "Vektor-Erweiterungen"
    RASTER_EXTENSIONS = "Raster-Erweiterungen"
    OUTPUT_CONFIG = "Ausgangskonfiguration"
    CONVERTER_FILE_TYPE = "Dateityp"
    SELECT_OUTPUT_FOLDER = "Ausgabeordner auswählen"

    # plugins/DividePointsByStripsPlugin.py
    DIVIDE_POINTS_BY_STRIPS_TITLE = "Punktvektor in Streifen aufteilen"
    DIVIDE_POINTS_BY_STRIPS_TOOLTIP = (
        "Bereitet die Konfiguration zur Segmentierung eines Punktlayers in Streifen vor.\n"
        "In dieser ersten Phase registriert das Werkzeug die Oberfläche,\n"
        "organisiert Betriebs- und Sensitivitätsparameter\n"
        "und lässt die Ausführung für die nächste Implementierungsphase bereit."
    )
    DIVIDE_POINTS_BY_STRIPS_INTRO = "Konfigurieren Sie den Punktlayer und die Anfangsparameter für die Streifenaufteilung."
    OPERATIONAL_PARAMETERS = "Betriebsparameter"
    SENSITIVITY_PARAMETERS = "Sensitivitätsparameter"
    UNIQUE_SEQUENTIAL_ID_FIELD = "Eindeutiges/fortlaufendes ID-Feld"
    TIMESTAMP_FIELD = "Zeitstempel-Feld"
    EXPECTED_POINT_FREQUENCY_SECONDS = "Erwartete Punktfrequenz (s)"
    EXPECTED_LATERAL_WIDTH_METERS = "Erwartete Seitenbreite (m)"
    AZIMUTH_MOVING_WINDOW = "Azimut-Mittelungsfenster"
    LIGHT_AZIMUTH_DEVIATION_THRESHOLD = (
        "Leichter Schwellenwert für Azimutabweichung (Grad)"
    )
    SEVERE_AZIMUTH_DEVIATION_THRESHOLD = (
        "Starker Schwellenwert für Azimutabweichung (Grad)"
    )
    MINIMUM_BREAK_SCORE = "Mindestpunktzahl für Unterbrechung"
    MINIMUM_POINT_COUNT = "Minimale Punktanzahl"
    TIME_TOLERANCE_MULTIPLIER = "Zeittoleranz (Multiplikator)"
    SELECT_POINT_VECTOR_LAYER = "Bitte einen Punkt-Vektorlayer auswählen."
    SELECT_FILE_BASED_POINT_LAYER = "Bitte einen dateibasierten Punktlayer auswählen."
    SELECT_REQUIRED_FIELDS = (
        "Bitte wählen Sie die erforderlichen ID- und Zeitstempelfelder aus."
    )
    SAVE_AND_STOP_EDITING_LAYER = "Speichern Sie die Ebene und beenden Sie den Editiermodus, bevor Sie dieses Werkzeug ausführen."
    SHOT_SEGMENTATION_COMPLETED = "Segmentierung abgeschlossen. Punkte: {total_points} | Streifen: {total_shots} | Gültig: {valid_shots} | Ungültig: {invalid_shots}"
    SHOT_SEGMENTATION_BUFFER_COMPLETED = "Segmentierung im Editierpuffer abgeschlossen. Punkte: {total_points} | Streifen: {total_shots} | Gültig: {valid_shots} | Ungültig: {invalid_shots}"
    DIVIDE_POINTS_BY_STRIPS_UI_ONLY_MESSAGE = "Die Oberfläche ist bereit. Die Streifenaufteilung wird in der nächsten Phase implementiert."

    # processing/RasterOptimizer.py
    RASTER_OPTIMIZER_TITLE = "Raster optimieren (Overviews)"
    RASTER_OPTIMIZER_TOOLTIP = (
        "Erstellt oder baut Pyramiden (Overviews) in TIFF-Rastern neu auf.\n"
        "Ermöglicht die Auswahl eines Ordners mit Rastern oder einzelner Layer,\n"
        "die Wahl der Overview-Ebenen, der Resampling-Methode\n"
        "und des Kompressionsalgorithmus (LZW, DEFLATE, ZSTD)."
    )
    INPUT_RASTER_LAYERS = "Eingabe-Rasterlayer"
    INPUT_RASTER_FOLDER = "Ordner mit Rastern"
    OVERVIEW_LEVELS = "Overview-Ebenen"
    RESAMPLING_METHOD = "Resampling-Methode"
    COMPRESS_OVERVIEW = "Overview-Kompression"
    PREDICTOR = "Prädiktor"
    ZLEVEL = "ZLevel (Kompression)"
    DELETE_EXISTING_OVERVIEWS = "Vorhandene Overviews vor dem Neuerstellen löschen"
    OVERVIEWS_CREATED_SUCCESS = "Overviews erfolgreich erstellt/aktualisiert."
    OVERVIEWS_ERROR = "Fehler beim Erstellen der Overviews: {error}"
    RASTER_OPTIMIZER_COMPLETED = "Rasteroptimierung abgeschlossen."
    USE_RECURSIVE_SEARCH = "Unterordner einbeziehen"
    SEARCHING_RASTERS = "Raster werden gesucht..."
    BIGTIFF_YES = "BIGTIFF erzwingen (erforderlich für Dateien >4GB)"
    RGB_MOSAIC_CREATOR_TITLE = "RGB-Mosaik-Ersteller"
    INPUT_RASTER_RED_BAND = "Rotband-Raster (R)"
    INPUT_RASTER_GREEN_BAND = "Grünband-Raster (G)"
    INPUT_RASTER_BLUE_BAND = "Blaudband-Raster (B)"
    BAND_RED_LABEL = "Band R"
    BAND_GREEN_LABEL = "Band G"
    BAND_BLUE_LABEL = "Band B"
    CREATE_ALPHA_BAND = "Alpha-Band für NoData erstellen"
    ALPHA_NODATA_VALUE = "NoData-Wert für Alpha"
    RGB_COMPOSITE = "RGB-Komposition"
    NDVI_CALCULATOR_TITLE = "NDVI-Rechner"
    INPUT_RASTER_NIR = "Nahes Infrarot-Raster (NIR)"
    INPUT_RASTER_RED = "Rot-Raster (RED)"
    BAND_NIR = "Band NIR"
    BAND_RED = "Band RED"
    SENTINEL_BANDS_INFO = "Sentinel-2: Band 8 (NIR) und Band 4 (Rot)"
    LANDSAT_BANDS_INFO = (
        "Landsat 8/9: Band 5 (NIR) und Band 4 (Rot) | "
        "Landsat 5/7: Band 4 (NIR) und Band 3 (Rot)"
    )
    NDVI = "NDVI"
    NDRE_CALCULATOR_TITLE = "NDRE-Rechner (Red Edge)"
    INPUT_RASTER_NIR_NDRE = "Nahes Infrarot-Raster (NIR) für NDRE"
    INPUT_RASTER_REDEDGE = "Red-Edge-Raster (RedEdge)"
    BAND_REDEDGE = "Band RedEdge"
    NDRE = "NDRE"
    GLI_CALCULATOR_TITLE = "GLI-Rechner (Green Leaf Index)"
    INPUT_RASTER_RGB_GLI = "Eingabe-RGB-Raster (3 oder 4 Bänder)"
    GLI = "GLI"
    GLI_STYLE_PATH = "Pfad zum GLI-QML-Stil"
    GLI_INTERPRETATION = (
        "GLI-Wert-Interpretation:\n"
        "  -1,0 bis 0,0  : Nackter Boden, Wasser, nicht bewachsene Flächen\n"
        "   0,0 bis 0,2  : Spärliche oder gestresste Vegetation\n"
        "   0,2 bis 0,5  : Moderate Vegetation\n"
        "   0,5 bis 1,0  : Dichte und gesunde Vegetation"
    )
    RGB_STYLE_STANDARDIZER_TITLE = "RGB-Stil standardisieren (Perzentil)"
    INPUT_RASTER_RGB = "Eingabe-RGB-Raster"
    RGB_STANDARDIZER_OUTPUT = "Standardisiertes RGB-Raster"
    SEGMENTATION_MODE = "Segmentierungsmodus"
    CURVE = "Kurve"
    STRAIGHT = "Gerade"
    BOTH_PATH = "Beide"
