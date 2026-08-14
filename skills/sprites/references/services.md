# Services

Use Sprites service tools for processes that must outlive a single exec call: web servers, workers, databases, watchers, and background daemons.

## Workflow

1. Identify the sprite and inspect existing services.
2. Reuse a service when its purpose and command clearly match; otherwise create a descriptive service.
3. Configure the correct working directory, command, and HTTP port.
4. Start the service and inspect its state and logs.
5. Verify the service URL without exposing private data.
6. Stop the service when the user asks or when clearly approved task cleanup requires it.

Treat every sprite URL as potentially internet-accessible. Do not serve environment variables, credentials, arbitrary file browsers, debug consoles, admin endpoints, stack traces, or unfiltered logs.

If a service is unreachable, check service state, logs, the listening port, and binding address before changing network policy. Servers normally need to listen on `0.0.0.0`, not only `127.0.0.1`, to be reachable through the sprite URL.
