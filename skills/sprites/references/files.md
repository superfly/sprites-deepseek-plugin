# Files in a sprite

Sprites MCP does not provide a dedicated write-file tool. Use `exec` deliberately.

## Preferred order

1. Use `git clone` for a real repository or substantial tree.
2. Use existing package or build commands when they generate the needed files.
3. For small generated content, base64-encode it locally and decode it remotely with a short `python3 -c` command.

Avoid heredocs and deeply nested shell quoting through MCP exec. They are fragile across JSON, shell, and command parsing layers.

After writing, verify the target with a narrow command such as `wc -c`, `sha256sum`, or a targeted read. Never print secrets merely to verify that a file exists.

For broad edits or generated trees, create a checkpoint first. Keep paths explicit and avoid destructive globs.
