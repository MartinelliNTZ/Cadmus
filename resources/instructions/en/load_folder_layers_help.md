# Load Folder Layers — Quick Guide

This tool scans a folder and its subfolders to load vector and raster files into the current QGIS project.

It can also:

- filter by file type;
- avoid reloading files that are already in the project;
- preserve the folder structure as layer groups;
- ignore the last folder level when creating groups;
- create a project backup before loading, when the project is already saved.

## How to use

1. Open `Cadmus > Load Folder Layers`.
2. Choose the root folder that contains the files.
3. Select one or more file types in the `File Types` section.
4. Adjust the extra options if needed:
- `Load only missing files`: skips files that are already loaded in the project.
- `Preserve folder structure`: creates groups in the layer tree based on subfolders.
- `Do not group last folder`: removes the last folder level before creating groups.
- `Create project backup if saved`: tries to create a project backup before loading.
5. Run the tool.

## What the plugin actually does

- Performs a recursive scan with `os.walk()` in the selected folder.
- Filters files by the extensions checked in the interface.
- Treats formats such as `shp`, `gpkg`, `geojson`, `kml`, `csv`, `gpx`, `tab`, `las`, and `laz` as vector data.
- Treats formats such as `tif`, `tiff`, `ecw`, `jp2`, and `asc` as raster data.
- Creates each layer through `ExplorerUtils.create_layer()`.
- Adds layers either to the project root or to groups, depending on the selected options.

## Group structure

- If `Preserve folder structure` is unchecked, all layers are added to the project root.
- If it is checked, the plugin uses the file folder's relative path to build nested groups.
- If `Do not group last folder` is enabled, the last folder segment is removed before creating the group.
- When the relative path becomes `.` or empty, the layer is added to the project root.

## Important behavior

- You must choose a valid folder.
- You must select at least one file type.
- The backup option is only enabled when the current project has already been saved to disk.
- `Load only missing files` compares the normalized file path against the sources of layers already loaded.

## Synchronous and asynchronous execution

- Up to 19 files, the tool runs synchronously.
- Above 19 files, it starts an asynchronous pipeline to reduce UI impact.
- In asynchronous mode, there is a dedicated progress dialog while layers are being added.
- If the user cancels, the process stops at the current point and layers already added remain in the project.

## When to use it

Use this tool when you need to load many files from a folder without adding them one by one manually.

It is especially useful for:

- projects organized by subfolders;
- recurring loads of updated data;
- folders that mix vector and raster files.

## Notes

- Review the selected file types before running the tool.
- If you want to keep the layer tree organized, use `Preserve folder structure`.
- If the folder contains many files, expect a partial load if you cancel midway.
