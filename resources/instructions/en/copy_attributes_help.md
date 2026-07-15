# Copy Attributes — Quick Guide

This tool selects fields from a source layer and adds them to the schema of a target layer.

Important: in the current code, it does not copy feature values. It only copies field structure, with name-conflict handling.

## How to use

1. Open `Cadmus > Copy Attributes`.
2. Choose the target layer.
3. Choose the source layer.
4. Select the desired source fields, or use the option for all fields.
5. Run the tool.

## What the plugin actually does

- Validates that source and target are vector layers.
- Requires the target layer to already be in editing mode.
- Lists fields based on the selected source layer.
- Lets you copy all fields or only selected ones.
- For each chosen field:
- if the field does not exist in the target, it is created;
- if the field already exists, the plugin asks how to resolve the conflict.

## Conflict handling

- `skip`: ignores the field that already exists.
- `rename`: creates a new field with a suffix such as `_1`, `_2`, and so on.
- `cancel`: stops the operation.

## Important behavior

- The tool does not transfer values between features.
- It also does not perform spatial matching or key-based matching between records.
- The main result is a schema change in the target layer.
- If no field is selected and the all-fields option is not enabled, the operation does not continue.

## When to use it

Use this tool when you want to prepare the target layer with new fields based on another layer's structure.

It is especially useful for:

- standardizing attribute schemas;
- creating missing fields before another processing step;
- replicating field names and types from a template layer.

## Notes

- Put the target layer in editing mode before running the tool.
- If you needed to copy values, this tool does not do that in the current code.
- Review field conflicts carefully to avoid creating unnecessary duplicate fields.
