# Authentication and setup

This bundle connects only to `https://sprites.dev/mcp`. Because DeepSeek Harness's current native HTTP MCP transport does not perform OAuth, the Cordis layer starts the pinned `mcp-remote` bridge over stdio. That bridge owns browser OAuth and local token storage.

## Healthy first run

1. The `sprites-mcp` Cordis row starts.
2. `mcp-remote` opens or prints a browser authorization URL.
3. The user signs in with Fly.io, chooses an organization, and selects connector access.
4. Harness discovers `mcp__sprites__*` tools.
5. `list_sprites` returns data or an empty list. Both mean authentication succeeded.

If the first tool synchronization times out while the user is authorizing, let the user finish OAuth and restart Harness. The stored OAuth session should be reused.

## Failure classes

### Tools missing

The bundle or Cordis row did not load. Check the composed config for `sprites-mcp`, then inspect Harness startup logs. Do not install a second MCP definition.

### OAuth incomplete

The tools may be absent or calls may report unauthorized. Keep Harness running, complete the browser flow, then retry once. If authorization finished after the initial MCP synchronization timed out, restart Harness.

### Prefix or visibility policy

Authentication works, but creates or listings are restricted by the connector token. Use API errors as the source of truth.

## Restricted versus full access

Restricted OAuth tokens require a non-empty name prefix and may cap sprite creation. The product default is often `mcp-`, but users can choose another prefix. Full access permits bare names and access to every sprite in the organization.

Rules:

1. Try a user-supplied name exactly once.
2. On an unambiguous required-prefix error, retry once with that prefix.
3. Report the actual created name.
4. Do not present Full access as a harmless way to remove a naming rule; it is organization-wide access.

## Forbidden workarounds

- Do not install or authenticate the Sprites CLI as a substitute for MCP OAuth.
- Do not ask for or paste API tokens into Harness configuration.
- Do not call the Sprites HTTP API directly.
- Do not register a duplicate MCP server.
- Do not clear all `mcp-remote` credentials without explaining that every connector using that store will be signed out.
