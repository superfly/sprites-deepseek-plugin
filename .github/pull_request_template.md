## Summary

<!-- What changed, and why does it belong in this plugin? -->

## Verification

<!-- List the checks you ran and any manual DeepSeek Harness/Sprites validation. -->

## Checklist

- [ ] I kept this change focused and updated relevant documentation.
- [ ] I added or updated semantic tests where behavior changed.
- [ ] `ruff check .` and `ruff format --check .` pass.
- [ ] `python scripts/check_repository.py` passes.
- [ ] `python -m unittest discover -s tests -v` passes.
- [ ] `node scripts/check_skill_entry.mjs` passes.
- [ ] I did not include credentials, OAuth caches, tokens, private data, or unredacted sensitive logs.
- [ ] I called out any MCP URL or attribution-header change because it invalidates existing OAuth sessions.
