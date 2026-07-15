# Drone Coordinates — Quick Guide

This tool reads drone MRK files and generates a point layer with the positions recorded during the flight.

It can also create a flight path line from those points, enrich the records with photo metadata, and save the outputs to files.

## How to use

1. Open `Cadmus > Drone Coordinates`.
2. Choose the folder that contains the MRK files.
3. Adjust the options if needed:
- `Search subfolders`: looks for MRKs inside subfolders.
- `Match photo metadata`: tries to enrich points with information from JPG images.
4. If needed, configure file output for points and track.
5. If needed, select QML files to style the points and the track.
6. Run the tool.

## What the plugin actually does

- Starts an asynchronous pipeline with `MrkParseStep`.
- Creates a point layer named `MRK_Pontos` from the parsed records.
- If the photo option is enabled, also runs `PhotoMetadataStep`.
- Can add extra fields such as file name, dates, image dimensions, camera model, ISO, aperture, and other metadata.
- Generates a line layer by connecting points grouped by `mrk_path` and `mrk_file`.
- Adds the generated layers to the project.
- Can save points and track to file with automatic renaming if the destination already exists.
- Can apply QML styles separately to points and track when enabled.

## Important behavior

- The tool works from a folder, not from an already loaded layer.
- Matching with photos depends on compatible images being available in folders related to the MRK files.
- If photo metadata is not found, points can still be generated without that enrichment.
- The main processing runs in the background.
- Points are always generated first; the track is derived from those points.

## Generated outputs

- MRK points as an in-memory layer or file.
- Flight track as an in-memory layer or file.
- Optional styling applied separately for points and line.

## When to use it

Use this tool when you want to convert MRK files into spatial products that can be viewed and analyzed in QGIS.

It is especially useful for:

- mapping photo positions from a flight;
- reconstructing the drone path;
- enriching points with technical image metadata.

## Notes

- Make sure the selected folder really contains valid MRK files.
- If you want photo matching, keep the folder structure consistent with the flight data.
- If you want persistent outputs, prefer saving as `gpkg`.
