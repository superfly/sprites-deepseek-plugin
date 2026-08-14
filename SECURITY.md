# Security policy

## Supported versions

Security fixes are applied to the latest release and the current `main` branch. Older plugin versions might not receive separate patches.

## Reporting a vulnerability

Do not report security vulnerabilities in a public issue, pull request, discussion, or Fly.io community post.

Use one of these private channels:

- Open a [private GitHub security advisory](https://github.com/superfly/sprites-deepseek-plugin/security/advisories/new).
- Email [security@fly.io](mailto:security@fly.io) with `sprites-deepseek-plugin` in the subject.

Include affected versions, reproduction steps, expected impact, and whether the issue concerns plugin instructions, Cordis composition, the OAuth bridge, the hosted Sprites MCP server, or an interaction with DeepSeek Harness. Do not send active tokens, browser cookies, OAuth cache files, or production data. If a minimal secret-like fixture is essential, use an obviously fake value.

Fly.io's security contact is also documented in the [Fly.io security documentation](https://fly.io/docs/security/#talk-to-the-security-team).

## Scope

This repository stores no Sprites credentials. The local `mcp-remote` process performs the browser OAuth flow and stores its cache outside this repository. Vulnerabilities in DeepSeek Harness or its bundled Cordis plugins should also be reported through DeepSeek's security process; issues in the hosted Sprites MCP service can be reported through the Fly.io channels above.
