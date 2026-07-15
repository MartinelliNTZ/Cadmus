class HtmlInstructions:
    def __init__(self, provider):
        self.provider = provider

    def get_raster_difference_statistics_help(self):
        return f"""
            {self.provider.logo}
            Cadmus-Werkzeug zur Berechnung von Unterschieden zwischen mehreren Rastern mit automatischen Statistiken und einem konsolidierten HTML-Bericht.
            {self.provider.transform_h('Ziel')}
            Unterschiede fuer alle moeglichen Rasterpaare berechnen.
            Variationen zwischen Oberflaechen identifizieren.
            Fuer jeden Vergleich automatische Statistiken erzeugen.
            {self.provider.transform_h('Verwendung')}
            1. Oeffnen Sie das Werkzeug.
            2. Geben Sie einen Rasterordner an oder waehlen Sie bereits in QGIS geladene Raster aus.
            3. Definieren Sie bei Bedarf die Ausgabe.
            4. Fuehren Sie es aus.
            {self.provider.transform_h('Ausgaben')}
            DIF_rasterA_rasterB.tif
            DIF_rasterA_rasterB_stats.html
            raster_difference_stats_summary.html
            {self.provider.transform_h('Hinweise')}
            Die Anzahl der Kombinationen waechst schnell.
            Es koennen viele Dateien erzeugt werden.
            Unterschiede verwenden nur Band 1.
            {self.provider.author_info}
        """

    def get_difference_fields_help(self):
        return f"""
            {self.provider.logo}
            Cadmus-Werkzeug zum Erzeugen von Differenzfeldern zwischen einem Basisfeld und anderen numerischen Feldern des Layers.
            {self.provider.transform_h('Ziel')}
            Die Differenz zwischen mehreren numerischen Attributen anhand eines Basisfelds als Referenz berechnen.
            {self.provider.transform_h('Verwendung')}
            1. Oeffnen Sie das Werkzeug.
            2. Waehlen Sie den Punkt-Layer.
            3. Definieren Sie das Basisfeld.
            4. Waehlen Sie bei Bedarf auszuschliessende Felder.
            5. Konfigurieren Sie Praefix und Genauigkeit.
            6. Fuehren Sie es aus.
            {self.provider.transform_h('Ausgaben')}
            Neue Felder mit dem definierten Praefix.
            {self.provider.transform_h('Hinweise')}
            Nicht numerische Felder werden ignoriert.
            Nullwerte erzeugen ein Null-Ergebnis.
            {self.provider.author_info}
        """

    def get_raster_mass_clipper_help(self):
        return f"""
            {self.provider.logo}
            Cadmus-Werkzeug fuer den Stapelzuschnitt von Rastern mit einem Polygon-Layer als Maske.
            {self.provider.transform_h('Ziel')}
            Mehrere Raster in einem einzigen Lauf zuschneiden.
            Zuschnitt nach gesamtem Layer oder nach Feature erlauben.
            Automatische Randkorrektur anwenden.
            {self.provider.transform_h('Verwendung')}
            1. Oeffnen Sie das Werkzeug.
            2. Definieren Sie die Polygonmaske.
            3. Waehlen Sie die Raster aus.
            4. Konfigurieren Sie Modus und Ausgabeordner.
            5. Fuehren Sie es aus.
            {self.provider.transform_h('Ausgaben')}
            raster_clip.tif
            raster_feat_1.tif
            {self.provider.transform_h('Hinweise')}
            Der Modus pro Feature kann viele Dateien erzeugen.
            Der Buffer vergroessert den zugeschnittenen Bereich leicht.
            {self.provider.author_info}
        """

    def get_geometry_difference_line_help(self):
        return f"""
            {self.provider.logo}
            Cadmus-Werkzeug zum Erzeugen von Linien zwischen Punkten und zur Berechnung von Distanzen.
            {self.provider.transform_h('Ziel')}
            Linien erzeugen, die zusammengehoerige Punkte verbinden.
            Distanzen zwischen Paaren berechnen.
            Vergleiche mit einem oder zwei Layern unterstuetzen.
            {self.provider.transform_h('Verwendung')}
            1. Oeffnen Sie das Werkzeug.
            2. Waehlen Sie Layer A.
            3. Aktivieren Sie bei Bedarf den zweiten Layer.
            4. Definieren Sie die Gruppierungsfelder.
            5. Fuehren Sie es aus.
            {self.provider.transform_h('Ausgaben')}
            Linien-Layer mit group_key, feature_a, feature_b und distance.
            {self.provider.transform_h('Hinweise')}
            Modus 2 erfordert Layer B und ein passendes Feld.
            Leere Geometrien werden ignoriert.
            {self.provider.author_info}
        """

    def get_grid_generator_help(self):
        return f"""
            {self.provider.logo}
            Cadmus-Werkzeug zum Generieren eines Punkt-, Linien- oder Polygonrasters innerhalb eines Polygon-Eingabebereichs.
            {self.provider.transform_h('Ziel')}
            Erstellen Sie ein regelmäßiges Raster basierend auf der Ausdehnung einer Eingabeebene.
            Extrahieren Sie nur die Zellen, die die Eingabeebene schneiden.
            {self.provider.transform_h('Verwendung')}
            1. Öffnen Sie das Werkzeug.
            2. Wählen Sie die Polygon-Eingabeebene.
            3. Legen Sie den horizontalen und vertikalen Abstand fest.
            4. Wählen Sie den Rastertyp.
            5. Aktivieren Sie das detaillierte Protokoll, wenn Sie Ausführungsdetails wünschen.
            6. Führen Sie es aus.
            {self.provider.transform_h('Ausgaben')}
            Rasterebene mit Punkt-, Linien- oder Polygongeometrie.
            {self.provider.transform_h('Hinweise')}
            Der Abstand steuert die Rasterdichte.
            Ungültige Geometrien können die Ausgabeabdeckung verringern.
            {self.provider.author_info}
        """

    def get_raster_mass_sampler_help(self):
        return f"""
            {self.provider.logo}
            Cadmus-Werkzeug fuer die Massenbeprobung mehrerer Raster an Punkten.
            {self.provider.transform_h('Ziel')}
            Werte aus mehreren Rastern an Punktpositionen extrahieren.
            Einen neuen Layer mit den beprobten Werten erzeugen.
            {self.provider.transform_alert('Raster-Namen muessen klar und eindeutig sein, da sie als Namen fuer Ausgabefelder verwendet werden.')}
            {self.provider.transform_h('Verwendung')}
            1. Oeffnen Sie das Werkzeug.
            2. Waehlen Sie die Eingabepunkte.
            3. Waehlen Sie die Raster aus.
            4. Definieren Sie bei Bedarf das Ausgabe-CRS.
            5. Fuehren Sie es aus.
            {self.provider.transform_h('Ausgaben')}
            Neuer Punkt-Layer mit einem zusaetzlichen Feld pro Raster.
            {self.provider.transform_h('Hinweise')}
            Werte ausserhalb der Rasterausdehnung ergeben Null.
            CRS-Unterschiede koennen die Genauigkeit beeinflussen.
            {self.provider.author_info}
        """

    def get_attribute_statistics_help(self):
        return f"""
            {self.provider.logo}
            Cadmus-Werkzeug zur Berechnung beschreibender Statistiken fuer numerische Attribute und zum CSV-Export.
            {self.provider.transform_h('Ziel')}
            Mittelwert, Median, Standardabweichung, Perzentile und weitere Statistiken berechnen.
            Ergebnisse nach CSV exportieren.
            {self.provider.transform_h('Verwendung')}
            1. Oeffnen Sie das Werkzeug.
            2. Waehlen Sie den Eingabe-Layer.
            3. Definieren Sie bei Bedarf auszuschliessende Felder.
            4. Passen Sie die Dezimalgenauigkeit an.
            5. Waehlen Sie die gewuenschten Statistiken.
            6. Konfigurieren Sie die Ausgabe und fuehren Sie es aus.
            {self.provider.transform_h('Ausgaben')}
            CSV-Datei mit einer Zeile pro analysiertem Feld.
            {self.provider.transform_h('Hinweise')}
            Es werden nur numerische Felder beruecksichtigt.
            Nullwerte werden ignoriert.
            {self.provider.author_info}
        """
