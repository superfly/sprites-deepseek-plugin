# Safety

## Destructive actions

Destroying a sprite permanently deletes its filesystem, services, checkpoints, and URL. Call the destroy tool only when the user explicitly asks to delete, destroy, or remove that sprite, or approves a clearly described cleanup.

Checkpoint restore replaces current filesystem state with the selected checkpoint. Confirm the sprite and checkpoint, and explain what newer state will be lost.

Create a checkpoint before risky package upgrades, migrations, broad refactors, or other changes where rollback is valuable.

## Public exposure

Treat sprite HTTP endpoints as potentially public. Never expose:

- Secrets, tokens, credentials, or environment dumps.
- Arbitrary file contents or directory browsers.
- Debug or administration interfaces without appropriate access controls.
- Unfiltered logs, stack traces, system paths, or user data.

## Network policy

Inspect network policy before modifying it. Only allow or block domains when the user asked for that policy change or the access is clearly necessary for the requested task. Prefer the narrowest domain set and explain the change.

## Authentication scope

Prefer restricted OAuth connector access with a non-empty prefix and creation cap. Full access is organization-wide and should be chosen only when the user intentionally needs it.
