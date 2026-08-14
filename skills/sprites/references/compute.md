# Remote compute workflow

Use this workflow for builds, tests, experiments, and isolated code execution.

1. Identify the sprite. List existing sprites and reuse a clear match; otherwise create a short task-scoped sprite.
2. Inspect the starting state with a small command such as `pwd`, `uname -a`, or a targeted directory listing.
3. Bring code in. Prefer `git clone` for repositories. For generated files, use the safe patterns in [files.md](files.md).
4. Install dependencies only when needed. Create a checkpoint first if installation or migration changes substantial state.
5. Run the narrowest relevant test or build before expanding scope.
6. Use a service rather than a forever-running exec for servers and workers; see [services.md](services.md).
7. Report the sprite name, important output, exit status, and any checkpoint or service id.

Do not assume the local Harness workspace is synchronized with the sprite. Files created locally do not appear remotely unless transferred through an explicit workflow.

For dependency or network failures, inspect the sprite network policy before changing it. Only allow domains required by the task.
