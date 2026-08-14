---
name: sprites
description: >
  Use Sprites from DeepSeek Harness for isolated remote compute: create and
  inspect persistent Linux environments, run commands and tests, manage
  long-running services, checkpoint and restore filesystem state, and inspect
  outbound network policy. Use when the user mentions Sprites, remote or cloud
  sandboxes, isolated agent compute, or asks to keep risky or long-running work
  off the local Harness workspace. Also use for Sprites MCP OAuth, prefix
  errors, setup checks, and missing Sprites tools.
---

# Sprites

Sprites are remote, isolated development environments with their own filesystem, URL, services, checkpoints, and network policy. DeepSeek Harness runs outside the sprite and uses the packaged Sprites MCP tools as its control plane.

## Golden path

1. Use `mcp__sprites__*` tools directly for sprite operations.
2. Keep the local Harness workspace and the remote sprite filesystem distinct.
3. An empty sprite list is authenticated success.
4. If tools are missing or OAuth is incomplete, read [auth-and-setup.md](references/auth-and-setup.md) and stop workaround attempts.
5. Every sprite-scoped tool requires a `sprite` argument containing the exact target name. If no target was named, list sprites and choose an obvious match; ask only when the choice is ambiguous.
6. Use services for long-running processes and one-off exec calls for short commands.
7. Create a checkpoint before risky remote changes.

Do not install the Sprites CLI, use raw Sprites HTTP APIs, invent tokens, or treat the Harness shell as though it were inside a sprite when the MCP path is unavailable.

## Tool map

The exact discovered names are server-qualified as `mcp__sprites__<rawName>`.

| Intent | Raw MCP tool | Target convention |
|---|---|---|
| List sprites | `list_sprites` | No sprite target |
| Create a sprite | `create_sprite` | Supplies the new name |
| Destroy a sprite | `destroy_sprite` | `sprite`: exact target name |
| Run a one-off command | `exec` | `sprite`: exact target name |
| Inspect or stop exec sessions | `exec_list`, `exec_kill` | `sprite`: exact target name |
| Inspect services | `service_list`, `service_get`, `service_logs` | `sprite`: exact target name |
| Manage services | `service_create`, `service_start`, `service_stop` | `sprite`: exact target name |
| Manage checkpoints | `checkpoint_create`, `checkpoint_list`, `checkpoint_get`, `checkpoint_restore` | `sprite`: exact target name |
| Inspect or change network policy | `policy_network_get`, `policy_network_update` | `sprite`: exact target name |

After listing or creating, reuse the exact sprite name returned by the server in every scoped call. There is no dedicated remote file-write tool. Read [files.md](references/files.md) before creating file content through exec.

## Common flows

### List

Call `mcp__sprites__list_sprites`. Summarize names, status, URLs, and useful identifiers; do not dump raw JSON unless requested. An empty list is success.

### Create

Use a short task-scoped name. Restricted OAuth connectors often require a prefix (commonly `mcp-`, but it may be custom). If the API returns a required prefix, retry once with that exact prefix and report the actual name. See [auth-and-setup.md](references/auth-and-setup.md).

### Run work

Use `mcp__sprites__exec` for short commands. For repository bootstrap, tests, and checkpoints, read [compute.md](references/compute.md). For long-running processes, read [services.md](references/services.md).

### Risky operations

Read [safety.md](references/safety.md). Destroy only with explicit delete/destroy/remove intent or clear cleanup approval. Restore is also destructive to current filesystem state, so confirm the target checkpoint and explain the effect.

## Response style

Lead with the operation and result. Include the sprite name, status, URL, service state, or checkpoint id that matters. Keep MCP registration and transport details out of ordinary operational updates.
