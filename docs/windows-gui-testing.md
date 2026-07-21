# Windows GUI smoke testing

The regular Windows workflow runs unit tests and builds the PyInstaller package. It does not prove that the packaged notification-area menu can be opened and operated by a user.

`powershell -File scripts/run-gui-smoke.ps1` builds the real `SPRIME-PM1-Battery-Tray.exe` and operates it through Windows UI Automation. Controls are selected by accessible names and control types rather than fixed screen coordinates.

## Scenarios

- the packaged tray application starts;
- Refresh now remains responsive;
- Show settings opens one responsive Settings window and it can be closed;
- Open logs opens the intended folder;
- all expected menu items exist and are enabled;
- a duplicate launch does not create duplicate tray processes;
- Quit exits cleanly;
- the application remains operable after a second launch.

The **Start on boot** item is checked for presence and enablement, but the smoke test does not toggle it.

## Self-hosted runner

Run this only on a dedicated Windows 11 VM or test machine. The runner must:

- run in a logged-in interactive desktop session, not as a Session 0 service;
- have the labels `self-hosted`, `windows`, `x64`, and `gui-automation`;
- permit interaction with the Windows taskbar and Explorer;
- have no copy of the packaged application already running.

Pull-request runs stay skipped until the repository variable below is enabled:

```text
GUI_SELF_HOSTED_ENABLED=true
```

Use `workflow_dispatch` for the first explicit run after registering the runner.

## Results

Success prints one `PASS` line per scenario. Failure exits non-zero and saves JSON plus a desktop screenshot under:

```text
test-results/windows-gui-smoke/
```

GitHub Actions uploads that directory only on failure.
