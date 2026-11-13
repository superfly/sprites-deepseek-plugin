# Changelog

All notable changes to this project are documented here.

## 0.2.0 - 2026-11-13

- Connect to the Fly MCP server at `https://mcp.fly.io` instead of `https://sprites.dev/mcp`, as part of the transition to the new Fly MCP server. The MCP server name and the `mcp__sprites__<tool>` tool names are unchanged.
- Existing users are signed out by this change and must complete the browser OAuth flow once more: the two endpoints have separate OAuth grants, and `mcp-remote` keys its cache on the server URL.

## 0.1.0 - 2026-08-14

- Add the DeepSeek Harness Cordis bundle for the hosted Sprites MCP server.
- Add browser OAuth through the pinned `mcp-remote` stdio bridge.
- Add a package-relative filesystem provider for the Sprites skill and references.
- Add repository validation, semantic tests, packaged-skill discovery, and CI.
- Add public contribution, support, conduct, security-reporting, ownership, and issue/PR guidance.
