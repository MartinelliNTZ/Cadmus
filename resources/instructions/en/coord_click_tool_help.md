# Capture Coordinates — Quick Guide

This tool lets you click on the map and open a panel with detailed information about the selected point.

In the same user flow, `CoordClickTool` captures the point and `CoorResultDialog` displays and updates the results.

## How to use

1. Activate `Cadmus > Capture Coordinates`.
2. Click anywhere on the map.
3. View the dialog with:
- WGS84 coordinates in decimal and DMS;
- UTM coordinates;
- zone, hemisphere, and EPSG;
- approximate altitude;
- approximate address.
4. Use the buttons to copy the information blocks you want.
5. Click another point on the map to update the same dialog.

## What the plugin actually does

- Captures the clicked coordinate using snapping when a valid snap exists on the canvas.
- Converts the point into geographic and UTM information.
- Opens the result dialog on the first click and then reuses the same window.
- Starts an asynchronous pipeline with two parallel tasks:
- reverse geocoding;
- altimetry lookup.
- If the pipeline fails, it falls back to separate tasks.
- Cancels previous tasks when the user clicks another point.

## What appears in the dialog

- Latitude and longitude in decimal.
- Latitude and longitude in DMS.
- UTM Easting and Northing.
- Zone, hemisphere, and EPSG.
- Approximate altitude.
- Municipality, intermediate region, state, region, and country.
- Buttons to copy WGS84, UTM, or the full location.

## Important behavior

- Basic coordinates appear first; address and altitude may take a few seconds.
- Without internet, the dialog still shows coordinates, but address and altitude may not load.
- The dialog uses the same `ToolKey` as the click tool, so the correct help file is `coord_click_tool_help.md`.
- The full-location copy button sends a text summary to the clipboard.

## When to use it

Use this tool when you need to inspect a map point quickly without creating a layer, feature, or annotation.

It is especially useful for:

- checking coordinates in more than one system;
- getting approximate point altitude;
- copying location data into reports, messages, or documents.

## Notes

- Altitude is approximate and depends on an external service.
- Address information depends on reverse geocoding coverage.
- Consecutive clicks cancel previous queries and prioritize the most recent point.
