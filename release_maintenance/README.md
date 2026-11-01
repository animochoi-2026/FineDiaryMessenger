# Release retention

Keep the three highest numeric versions PER CHANNEL: newest + two previous.
Channels are identified by the exact stable/test ZIP asset names, NOT by the
GitHub prerelease label. Promoted releases belong to both. Retain the union of
both keep sets, so frequent test builds can never evict stable releases.
Deploy this maintenance change BEFORE publishing separate test assets.

The GitHub Actions workflow runs after release publication, daily at 18:17 UTC
(03:17 Korea time), or manually. Manual runs default to a read-only preview.
The daily fallback handles delayed uploads and releases published using
GITHUB_TOKEN, which do not necessarily trigger a second workflow.

Before removing anything, all three retained releases must have an uploaded
Windows ZIP with a GitHub SHA-256 digest and an uploaded checksum file. Missing
files, duplicate numeric versions, API errors, or concurrent release changes
stop cleanup. Upload validation is not an application functionality test.

Only old release records and their attached assets are deleted. Git tags,
commits, README, desktop installations, config, profiles, data, and local build
archives remain untouched. Deleted releases will no longer be offered for
rollback by the app. Recovery of installers requires a separately saved copy.

Drafts and non-numeric tags are outside this policy. The repository is explicitly
restricted to animochoi-2026/FineDiaryMessenger, with only a job-scoped GitHub
token. No token is included in the distributed desktop application.

Read-only local check:

```powershell
.\venv\Scripts\python.exe -B release_maintenance/prune_releases.py
```

On GitHub: Actions → Keep latest 3 releases → Run workflow. Leave `apply`
unchecked to preview; check it only to actually delete older releases/assets.

Public repository deployment is limited to `.github/workflows/release-retention.yml`
and `release_maintenance/`. Do not push the private desktop application source,
configuration or student data into the release repository.

## Deployment verification (2026-09-28)

Activated on the public repository's `main` branch in workflow commit
`b5244dd69352345d4e93e62938c2265f2bc1ff25`. Uploaded script and workflow contents
were compared against these local, tested files before execution.

First approved apply run succeeded:
https://github.com/animochoi-2026/FineDiaryMessenger/actions/runs/36435847788

Remaining releases: v11.3.0, v11.2.0, v11.1.1 (each with ZIP and checksum).
Removed releases/assets: v11.1.0, v11.0.0, v10.0.0. All six Git tags remain.
No desktop update is needed: this policy runs on GitHub, not in the app.
