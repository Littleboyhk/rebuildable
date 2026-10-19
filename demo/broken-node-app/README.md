# Broken Node app

This fixture is intentionally **not** a working application. It keeps valid
project metadata and a README so a future rebuildable scanner can award two
checks before it reports the useful failures:

- `src/start.js` asks for `missing-config`, which is not present.
- `start.js` includes a debug log and an unresolved `TODO` marker.
- `package.json` points its `main` field at a missing entrypoint.
- There is no test file or dependency lockfile yet.
- `.env` is a local configuration file; its value is harmless demo data, but
  the file still belongs outside a committed project tree.

The clean signals are the absence of credential-shaped values and this README.
Run it from the repository root with `bash demo/run_demo.sh`. The demo keeps
the expected failures visible and exits successfully so it can be used as a
fixture walkthrough.
