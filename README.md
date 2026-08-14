# Sprites for DeepSeek Harness

[![CI](https://github.com/superfly/sprites-deepseek-plugin/actions/workflows/ci.yml/badge.svg)](https://github.com/superfly/sprites-deepseek-plugin/actions/workflows/ci.yml)
[![Latest tag](https://img.shields.io/github/v/tag/superfly/sprites-deepseek-plugin?label=version)](https://github.com/superfly/sprites-deepseek-plugin/tags)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Use [Sprites](https://sprites.dev) from [DeepSeek Harness](https://deepseek.com/harness/en/): isolated, persistent Linux environments for builds, tests, experiments, and long-running services.

This repository is a Harness bundle. Its `cordis.patch.yml` mounts:

- `@deepseek-ai/dsh-mcp-client`, connected to the hosted Sprites MCP server.
- This package's `index.js` entry, which mounts `@deepseek-ai/dsh-skill-filesystem` against the packaged Sprites workflow skill.

The result is a native Cordis composition: Sprites tools appear as `mcp__sprites__*`, and the Sprites skill is discoverable through Harness's normal skill system.

## Requirements

- Node.js 20.19 or newer. The packaged filesystem provider currently depends on Chokidar 5, whose engine floor is Node 20.19.
- DeepSeek Harness developer preview.
- Browser access for the first Sprites OAuth authorization.
- Network access for `npx` to run the pinned `mcp-remote@0.1.38` OAuth bridge.

Harness's current Streamable HTTP MCP transport accepts static headers but does not perform MCP OAuth. This bundle therefore uses Harness's supported stdio transport and `mcp-remote` to complete the standard browser OAuth flow without requiring a Sprites API token.

## Install

Install the GitHub checkout into the profile you use. For the built-in Web profile:

```sh
npx @deepseek-ai/dsh plugin --profile web add github:superfly/sprites-deepseek-plugin
```

Then start that profile:

```sh
npx @deepseek-ai/dsh --profile web
```

On first connection, complete the browser OAuth flow, choose the Fly.io organization, and review the connector access policy. Restart Harness once if the initial tool synchronization timed out while you were authorizing.

For local development from this repository:

```sh
npx @deepseek-ai/dsh plugin --profile web add .
npx @deepseek-ai/dsh --profile web
```

To try the layer without installing it into a profile:

```sh
npx @deepseek-ai/dsh web --patch ./cordis.patch.yml
```

Verify the installed bundle and composed rows without booting the UI:

```sh
npx @deepseek-ai/dsh --profile web --dump-config
```

The output should include the `dsh-sprites-plugin` layer, `sprites-mcp`, and `sprites-skill-filesystem`.

## First prompts

- "List my sprites."
- "Create a sprite for this experiment and run `uname -a` in it."
- "Create a checkpoint, then run the test suite in my sprite."
- "Start the web service in my sprite and give me its URL."

An empty sprite list is a successful authenticated response.

## Authentication and access

The hosted endpoint is `https://sprites.dev/mcp` and uses OAuth 2.1. `mcp-remote` stores its OAuth state in its normal local credential directory; this repository contains no credentials.

The Sprites consent screen normally creates a restricted connector token. Its default name prefix is often `mcp-`, and it may cap how many sprites the connector can create. A custom non-empty prefix remains restricted. Choosing **Full access** removes the prefix restriction but grants access to every sprite in the organization.

Prefer restricted access for agent work. If a create call reports a required prefix, Harness should retry once with that exact prefix and report the actual name.

## How it works

`cordis.patch.yml` contributes two rows:

1. `sprites-mcp` starts `mcp-remote` through the Harness MCP client. The bridge handles OAuth and exposes server tools through `ctx.tools` as `mcp__sprites__<tool>`.
2. `sprites-skill-filesystem` loads this package's `index.js`. The entry resolves `skills/` from `import.meta.url`, then mounts `@deepseek-ai/dsh-skill-filesystem` as an isolated provider. This is intentionally done in JavaScript: a bundle patch is evaluated with the profile directory as its `baseUrl`, not the installed package directory.

The MCP subprocess also sends fixed, privacy-safe client attribution headers:

| Header | Value |
|---|---|
| `Fly-Client-Agent` | `deepseek-harness` |
| `Fly-Client-Interactive` | `false` |

No user-, machine-, repository-, or session-specific attribution is sent. The headers are advisory analytics only and are not used for authorization or rate limiting.

`mcp-remote` includes both the server URL and serialized headers in its OAuth cache key. Changing either attribution header therefore invalidates existing cached authorization and requires users to authenticate again.

## Safety

- Treat services exposed through a sprite URL as potentially internet-accessible.
- Never publish secrets, environment dumps, arbitrary files, debug endpoints, or unfiltered logs.
- Use a checkpoint before risky filesystem changes, dependency upgrades, or migrations.
- Destroying a sprite is irreversible. Only destroy one when the user explicitly asks to delete, destroy, or remove it, or approves cleanup.
- Inspect outbound network policy before changing it.

## Troubleshooting

### Tools are missing

Confirm the bundle appears in `--dump-config` and that both Cordis rows are present. Harness's MCP client logs connection, discovery, and tool-registration failures. The native tool names begin with `mcp__sprites__`.

### OAuth did not finish

Keep the Harness process running while completing the browser flow. If initial synchronization times out, finish authorization and restart Harness; `mcp-remote` reuses the stored OAuth session.

For persistent `mcp-remote` authentication state problems, follow its upstream troubleshooting guidance. Clearing its credential directory signs every `mcp-remote` connector out, so do not do that casually.

### `npx` cannot start

Make sure Node.js 20.19+ and `npx` are available in the environment that launches Harness. The MCP client intentionally uses argument arrays without shell interpolation.

### Network failures inside a sprite

Ask Harness to inspect the sprite's network policy before changing it. A reachable MCP server does not imply unrestricted egress inside a sprite.

## Repository layout

```text
package.json                 Harness bundle manifest (`dsh.bundle`)
cordis.patch.yml             Cordis rows for MCP and packaged skills
index.js                     Package-relative Sprites skill provider entry
skills/sprites/              DeepSeek Harness Sprites skill and references
scripts/check_repository.py  Static repository validation
tests/test_repository.py     Bundle contract tests
```

## Development

```sh
python -m pip install -r requirements-dev.txt
npm install --ignore-scripts --package-lock=false
ruff check .
ruff format --check .
python scripts/check_repository.py
python -m unittest discover -s tests -v
node scripts/check_skill_entry.mjs
```

## Related

- [DeepSeek Harness plugin development](https://deepseek-harness.github.io/deepseek-harness/en/develop/basic/)
- [DeepSeek Harness package and install guide](https://deepseek-harness.github.io/deepseek-harness/en/develop/basic/publish)
- [Sprites remote MCP documentation](https://docs.sprites.dev/integrations/remote-mcp/)
- [Sprites MCP server repository](https://github.com/superfly/sprites-mcp)
- [`mcp-remote`](https://github.com/geelen/mcp-remote)

## Support and feedback

- Report reproducible plugin bugs with the [bug report form](https://github.com/superfly/sprites-deepseek-plugin/issues/new?template=bug_report.yml).
- Propose workflow or integration improvements with the [feature request form](https://github.com/superfly/sprites-deepseek-plugin/issues/new?template=feature_request.yml).
- Ask general Sprites questions in the [Fly.io community](https://community.fly.io/) after checking the [Sprites documentation](https://docs.sprites.dev/).
- Report security issues privately as described in [SECURITY.md](SECURITY.md). Never include credentials or production data in an issue.

## Project policies

See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), [SECURITY.md](SECURITY.md), [SUPPORT.md](SUPPORT.md), and [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](./LICENSE) © Fly.io, Inc.
