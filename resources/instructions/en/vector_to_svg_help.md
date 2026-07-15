# Vector to SVG Converter - Quick Guide

This tool exports a QGIS vector layer to SVG, honoring background, border, label, and per-feature export options.

## How to use

1. Open `Cadmus > Vector to SVG Converter`.
2. Select the input vector layer.
3. If needed, enable `Only selected features`.
4. Configure background color, border color/width, and label color/size.
5. Enable or disable transparent background, border, label, and one-SVG-per-feature options.
6. Choose the output folder or use the project folder.
7. Run the tool.

## What the plugin actually does

- Validates that the input is a valid vector layer with features.
- Uses only selected features when that option is enabled.
- Reprojects geometries to WGS84 before building the SVG.
- Exports either a single SVG for the whole layer or one SVG per feature.
- Applies either a transparent background or a solid background color.
- Controls geometry borders using the user-defined color and width.
- Tries to draw real layer labels from QGIS labeling settings, with fallback to `displayExpression()` and the `Name` field.

## File naming

- Single SVG export uses the QGIS layer name.
- Per-feature export:
  - uses the `Name` field when it exists and has a value;
  - otherwise uses `LayerName_1`, `LayerName_2`, `LayerName_3`...
- If a file already exists, the plugin creates an incremental name instead of overwriting it.

## Important behavior

- When `Transparent background` is enabled, no fill background is written to the SVG.
- When `Show border` is disabled, geometry outlines are not drawn.
- When `Show label` is disabled, no text is exported.
- Label size can be controlled directly in the tool.
- The final result is always written to disk in the selected folder.

## When to use it

Use this tool when you want to:

- generate SVG icons or figures from project vectors;
- export features individually for layout, web, or automation usage;
- reuse basic layer symbology in a lightweight vector output.

## Notes

- Review the layer labeling setup if you expect labels to appear.
- Layers with many features may generate many files when per-feature export is enabled.
- For cleaner filenames, it is recommended to populate the `Name` field before exporting one SVG per feature.
