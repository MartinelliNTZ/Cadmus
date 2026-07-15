# Export All Layouts — Quick Guide

This tool exports all layouts from the current project to PDF, PNG, or both formats.

It can also:

- merge all exported PDFs into one final file;
- convert exported PNGs into a single PDF;
- avoid overwriting by creating suffixed file names;
- save the options used in the dialog.

## How to use

1. Open `Cadmus > Export All Layouts`.
2. Select at least one output format: `Export PDF` and/or `Export PNG`.
3. Adjust the extra options if needed:
- `Merge PDF`: combines exported PDFs into `_PDF_UNICO_FINAL.pdf`.
- `Merge PNG`: converts exported PNGs into a final PDF named `_PNG_MERGED_FINAL.pdf`.
- `Replace Existing`: overwrites existing files.
- `Max Width`: sets the maximum width used in the PDF generated from PNGs.
4. Choose the output folder.
5. If you want to use the project folder, click the button that points to `.../exports`.
6. Click `Export`.

## What the plugin actually does

- Reads every layout from the current project through `layoutManager().layouts()`.
- Creates the output folder automatically if it does not exist.
- Removes invalid characters from each layout name before generating files.
- When `Replace Existing` is unchecked, creates names like `Layout_1`, `Layout_2`, and so on to avoid conflicts.
- Exports each layout individually with `QgsLayoutExporter`.
- Shows a progress dialog while processing.
- Lets you cancel the export while it is running.
- Displays a final summary with successes, errors, and the destination folder.

## Optional dependencies

- `PyPDF2` is only needed when `Merge PDF` is enabled.
- `Pillow` is only needed when `Merge PNG` is enabled.
- If a dependency is missing, the plugin asks for confirmation before installing it.
- If you decline the installation, the export continues without that merge step.

## Important behavior

- At least one export format must be selected.
- The plugin counts a layout as successful if at least one selected format is exported successfully.
- If one format fails and the other succeeds, the error still appears in the final summary.
- Canceling stops the loop at the current point; files already exported remain in the folder.

## When to use it

Use this tool when you need to export every layout in a project without opening and saving them one by one.

It is especially useful for:

- delivering a complete sheet set;
- generating batch revisions;
- consolidating PDF output into one final file.

## Notes

- Review the output folder before running the tool, especially if `Replace Existing` is enabled.
- If several layouts have similar names, check the generated files after export.
- For large projects, consider exporting first without merge to validate the results.
