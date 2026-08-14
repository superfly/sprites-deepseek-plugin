# Contributing

Thanks for helping improve Sprites for DeepSeek Harness. By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Before opening a change

- Search existing issues and pull requests before filing a duplicate.
- Use the bug or feature issue form for changes that need design discussion.
- Do not open a public issue for a security vulnerability; follow [SECURITY.md](SECURITY.md).

Small, focused pull requests are easiest to review. Explain the user-facing problem, why the change belongs in this plugin, and any DeepSeek Harness, Cordis, MCP, or Sprites contract assumptions it introduces.

## Pull requests

1. Fork or branch from `main`.
2. Make the smallest coherent change.
3. Add or update semantic tests and documentation.
4. Run the development checks below.
5. Open a pull request and complete its checklist.

Contributions are licensed under the repository's [MIT License](LICENSE). By submitting a contribution, you agree that it may be distributed under that license.

## Development checks

Use Node.js 20.19 or newer, then run:

```sh
python -m pip install -r requirements-dev.txt
npm install --ignore-scripts --package-lock=false
ruff check .
ruff format --check .
python scripts/check_repository.py
python -m unittest discover -s tests -v
node scripts/check_skill_entry.mjs
```

Changes to the Cordis patch, package entry, MCP transport, OAuth headers, dependency versions, tool names, or skill root must include a regression test. Keep `@deepseek-ai/dsh-mcp-client` and `@deepseek-ai/dsh-skill-filesystem` declared directly rather than relying on Harness's transitive dependencies.

The `mcp-remote` OAuth cache key includes the server URL and serialized headers. Changing either attribution header signs existing users out and must be called out in the changelog and pull request.

Do not commit tokens, OAuth credential caches, browser cookies, logs containing secrets, or generated test data. End-to-end tests must use a restricted connector and non-production data.

## Review and merging

Pull requests must pass required CI and resolve review conversations. Maintainers generally squash-merge changes and delete merged branches.
