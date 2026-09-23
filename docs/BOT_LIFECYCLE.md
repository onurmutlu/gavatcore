# SaaS bot lifecycle

## Supported runtime

Use one API worker and one replica, with the complete repository available.
Do not use Uvicorn reload while bots run. The API process owns its child
process handles; there is no distributed supervisor or durable PID registry.
The production Docker command now uses one worker. An API-only container
without the root `userbot_session.py`, `handlers`, `utils`, and `infrastructure`
cannot run userbots; container packaging is not validated by this change.

From the repository root, after installing API and userbot dependencies and
configuring the environment:

```bash
PYTHONPATH="$PWD:$PWD/gavatcore-api" python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

`main.py` is the separate legacy userbot manager. There is no `start.py` and
`main.py` does not implement `--all`, `--bot`, or `--api`.

## Behavior

- The launcher uses the running Python interpreter and absolute runner/config
  paths; session paths are explicit rather than inferred from the child cwd.
- Telegram login must already be complete for that session file. Missing
  authorization fails; a web request never waits for terminal OTP/2FA input.
- A child reports readiness only after authorization and handler setup.
  The API start call returns at readiness, not when the bot eventually exits.
  This is startup readiness, not a continuous Telegram connectivity heartbeat.
- A per-bot lock serializes start/stop. Duplicate starts on a running owned
  process are idempotent. Restart awaits real termination before starting again.
- Stop sends terminate, waits up to 10 seconds, then kills and reaps if needed.
  Only after confirmed exit is the database marked inactive/offline.
- Unexpected exits use a newly opened database session. No background monitor
  retains an HTTP request's database session or ORM object.
- Graceful API shutdown terminates owned children before disposing the DB engine.
- Child output is drained without unbounded retention; stderr is discarded.
  Startup failures expose a generic diagnostic, not child logs or secrets.
- Generated configuration files have mode 0600 and contain no API keys.
  Credentials are passed through the child environment.

## Recovery limits

After a hard API crash, children may outlive their supervisor. If a DB row is
active but the process is not owned by this worker, start/stop refuses to claim
success. An operator must identify and stop the orphan process, verify that
it exited, then reconcile the row before restarting it. Never clear an active
flag blindly or launch another process against the same session file.

Multi-worker/multi-host support, durable recovery, Telegram onboarding, and
heartbeat reconciliation require a separate worker/supervisor design. This
patch does not make the whole SaaS production-ready. Creating a new bot without
an authorized session will fail to launch; the inactive/error row remains.

## Verification

```bash
python -m unittest discover -s gavatcore-api/tests -v
python -m compileall -q gavatcore-api/app userbot_session.py
```

The subprocess tests launch real local Python children, including a child that
ignores SIGTERM. Service/session tests execute the production classes with
external dependencies isolated; they do not establish SQLAlchemy or Telegram
integration compatibility. Full API import, PostgreSQL, Docker builds, live
Telegram login, and message delivery have not been tested in this environment.
