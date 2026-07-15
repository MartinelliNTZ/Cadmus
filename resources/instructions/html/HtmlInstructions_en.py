class HtmlInstructions:
    def __init__(self, provider):
        self.provider = provider

    def get_raster_difference_statistics_help(self):
        return f"""
            {self.provider.logo}
            Cadmus tool for calculating differences between multiple rasters, with automatic statistics and a consolidated HTML report.
            {self.provider.transform_h('Objective')}
            Calculate differences for every possible raster pair.
            Identify variations between surfaces.
            Generate automatic statistics for each comparison.
            {self.provider.transform_h('How to use')}
            1. Open the tool.
            2. Provide a raster folder or select rasters already loaded in QGIS.
            3. Define the output if needed.
            4. Run.
            {self.provider.transform_h('Outputs')}
            DIF_rasterA_rasterB.tif
            DIF_rasterA_rasterB_stats.html
            raster_difference_stats_summary.html
            {self.provider.transform_h('Warnings')}
            The number of combinations grows quickly.
            It may generate many files.
            Differences use band 1 only.
            {self.provider.author_info}
        """

    def get_difference_fields_help(self):
        return f"""
            {self.provider.logo}
            Cadmus tool for generating difference fields between a base field and other numeric fields in the layer.
            {self.provider.transform_h('Objective')}
            Calculate the difference between several numeric attributes using a base field as reference.
            {self.provider.transform_h('How to use')}
            1. Open the tool.
            2. Select the point layer.
            3. Define the base field.
            4. Choose fields to exclude if needed.
            5. Configure prefix and precision.
            6. Run.
            {self.provider.transform_h('Outputs')}
            New fields created with the chosen prefix.
            {self.provider.transform_h('Warnings')}
            Non-numeric fields are ignored.
            Null values generate null output.
            {self.provider.author_info}
        """

    def get_raster_mass_clipper_help(self):
        return f"""
            {self.provider.logo}
            Cadmus tool for batch clipping rasters using a polygon layer as mask.
            {self.provider.transform_h('Objective')}
            Clip multiple rasters in a single run.
            Allow clipping by whole layer or by feature.
            Apply automatic edge correction.
            {self.provider.transform_h('How to use')}
            1. Open the tool.
            2. Define the polygon mask.
            3. Select the rasters.
            4. Configure mode and output folder.
            5. Run.
            {self.provider.transform_h('Outputs')}
            raster_clip.tif
            raster_feat_1.tif
            {self.provider.transform_h('Warnings')}
            Per-feature mode may generate many files.
            The buffer slightly expands the clipped area.
            {self.provider.author_info}
        """

    def get_geometry_difference_line_help(self):
        return f"""
            {self.provider.logo}
            Cadmus tool for creating lines between points and calculating distances.
            {self.provider.transform_h('Objective')}
            Generate lines connecting related points.
            Calculate distance between pairs.
            Support comparison using one or two layers.
            {self.provider.transform_h('How to use')}
            1. Open the tool.
            2. Select layer A.
            3. Enable the second layer if needed.
            4. Define grouping fields.
            5. Run.
            {self.provider.transform_h('Outputs')}
            Line layer with group_key, feature_a, feature_b and distance.
            {self.provider.transform_h('Warnings')}
            Mode 2 requires layer B and a matching field.
            Empty geometries are ignored.
            {self.provider.author_info}
        """

    def get_grid_generator_help(self):
        return f"""
            {self.provider.logo}
            Cadmus tool for generating a point, line or polygon grid inside a polygon input area.
            {self.provider.transform_h('Objective')}
            Generate a regular grid using the extent of an input layer.
            Extract only the cells that intersect the input polygon.
            {self.provider.transform_h('How to use')}
            1. Open the tool.
            2. Select the polygon input layer.
            3. Set horizontal and vertical spacing.
            4. Choose the grid type.
            5. Enable verbose log if you want execution details.
            6. Run.
            {self.provider.transform_h('Outputs')}
            Grid layer with point, line or polygon geometry.
            {self.provider.transform_h('Warnings')}
            Spacing controls the grid density.
            Invalid geometries may reduce output coverage.
            {self.provider.author_info}
        """

    def get_raster_mass_sampler_help(self):
        return f"""
            {self.provider.logo}
            Cadmus tool for mass sampling multiple rasters over points.
            {self.provider.transform_h('Objective')}
            Extract values from several rasters at point locations.
            Generate a new layer with sampled values.
            {self.provider.transform_alert('Raster names must be clear and unique because they will be used as output field names.')}
            {self.provider.transform_h('How to use')}
            1. Open the tool.
            2. Select the input points.
            3. Select the rasters.
            4. Define output CRS if needed.
            5. Run.
            {self.provider.transform_h('Outputs')}
            New point layer with one additional field per raster.
            {self.provider.transform_h('Warnings')}
            Values outside raster extent return null.
            CRS differences may affect precision.
            {self.provider.author_info}
        """

    def get_attribute_statistics_help(self):
        return f"""
            {self.provider.logo}
            Cadmus tool for calculating descriptive statistics for numeric attributes and exporting CSV.
            {self.provider.transform_h('Objective')}
            Calculate mean, median, standard deviation, percentiles and other statistics.
            Export results to CSV.
            {self.provider.transform_h('How to use')}
            1. Open the tool.
            2. Select the input layer.
            3. Define fields to exclude if needed.
            4. Adjust decimal precision.
            5. Choose the desired statistics.
            6. Configure output and run.
            {self.provider.transform_h('Outputs')}
            CSV file with one row per analyzed field.
            {self.provider.transform_h('Warnings')}
            Only numeric fields are considered.
            Null values are ignored.
            {self.provider.author_info}
        """
