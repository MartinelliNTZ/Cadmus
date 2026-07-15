# Cadmus Settings — Quick Guide

This tool centralizes global preferences used by parts of the Cadmus plugin.

In the current code, it lets you:

- choose the default vector calculation method;
- define numeric precision for vector fields;
- define the feature threshold for asynchronous processing;
- open the local Cadmus preferences folder.

## How to use

1. Open `Cadmus > Configuracoes Cadmus`.
2. Choose the vector calculation method:
- `Ellipsoidal`
- `Cartesian`
- `Both`
3. Adjust the vector field precision.
4. Adjust the asynchronous threshold.
5. Click `Save`.

## What the plugin actually does

- Loads saved preferences with `load_tool_prefs()`.
- Saves the settings under the `settings` preference key.
- Shows a confirmation message after saving.
- Closes the window right after applying the preferences.
- Lets you open the local folder where preference files are stored.

## What each option means

- `Vector calculation method`: defines the text stored in `calculation_method`.
- `Vector fields precision`: stores an integer value in `vector_field_precision`.
- `Async threshold`: stores an integer value in `async_threshold_features`.

## Important behavior

- The current asynchronous threshold is measured in number of features, not in MB.
- Precision accepts values from 0 to 10.
- The asynchronous threshold accepts values from 1 to 100000000.
- The code still reads the old `async_threshold_bytes` key for backward compatibility, but now uses the feature-based limit.
- This plugin only saves preferences; it does not run vector calculations by itself.

## Preferences folder

- The interface link tries to open `PREF_FOLDER` in the operating system.
- If the folder does not exist, the plugin shows a warning instead of opening the file explorer.

## When to use it

Use this tool when you want to adjust the default behavior of other Cadmus tools that depend on these global preferences.

## Notes

- Change the calculation method only if it fits your workflow.
- If you lower the asynchronous threshold too much, more operations may run in the background.
- If behavior becomes unexpected after changing preferences, review the files stored in the preferences folder.
