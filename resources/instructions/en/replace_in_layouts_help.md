# Replace Text in Layouts — Quick Guide

This tool searches for text in project layout labels and replaces it with a new value.

In the current code, it works on items of type `QgsLayoutItemLabel`.

## How to use

1. Open `Cadmus > Replace Text in Layouts`.
2. Enter the text to search for.
3. Enter the new text.
4. If needed, use the swap button to invert both fields.
5. Adjust the options:
- `Case Sensitive`: matches uppercase and lowercase exactly.
- `Full Label Replace`: replaces the entire label text when a match is found.
6. Run the tool and confirm the destructive operation.

## What the plugin actually does

- Saves the last entered values and selected options in preferences.
- Requires the search field to be non-empty.
- Shows a confirmation dialog before changing layouts.
- If the project is already saved on disk, creates a `.qgz` backup inside the `backup` folder.
- Iterates through all layouts in the project.
- Inside each layout, changes only items that are `QgsLayoutItemLabel`.
- At the end, shows a summary with the number of analyzed layouts and applied changes.

## How replacement works

- With `Case Sensitive` enabled, matching respects uppercase and lowercase.
- With `Case Sensitive` disabled, matching ignores case differences.
- With `Full Label Replace` disabled, the plugin performs a partial replacement inside the label text.
- With `Full Label Replace` enabled, the plugin replaces the whole label content with the new text whenever a match is found.

## Important behavior

- The tool does not change other layout item types; it works only on labels.
- A backup is created only if the project has already been saved.
- If the project is not saved, the tool can still run, but without backup creation.
- The final summary reports counts, not a detailed per-item change list.

## When to use it

Use this tool when you need to update repeated text quickly across multiple layouts in the same project.

It is especially useful for:

- changing year, client name, or responsible person;
- updating standard text across many layouts;
- correcting repeated terms without editing labels one by one.

## Notes

- Review the search text carefully to avoid overly broad replacements.
- Use `Full Label Replace` only when you want to replace the entire label content.
- If the project is important, save it before running so the backup can be created.
