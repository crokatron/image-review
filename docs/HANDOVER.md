# Image Review: maintainer handover

[One-screen summary](START-HERE.md) · [User manual](USER-MANUAL.md) · [Feature overview](../README.md) · [Recorded validation](../VALIDATION.md)

## Purpose and behaviour to preserve

Review an image collection one item at a time and retain reversible decisions. Separate passes support manually tagging people, deciding meme/not-meme and reviewing adult-content labels. Machine suggestions help choose a queue but do not silently replace a person’s saved decision.

- **Review passes:** Separate people, meme and adult-content workflows. (Owner-only review.)
- **Queues and filters:** Choose source bands, reviewed/unreviewed status, people and machine suggestion filters. (Owner-only review.)
- **Fast decisions:** Use large buttons or supported swipe gestures; skip uncertain items. (Owner-only review.)
- **Undo and resume:** Keep independent histories, retry a failed save and resume across devices. (Owner-only review.)
- **Learning:** Use eligible human meme labels to update a constrained final decision filter. (Owner-only review.)
- **Exports:** Export decisions and reversible history; original images remain untouched. (Owner-only review.)

The [demo](../demo.html) is a smaller, labelled simulation with fictional data. It explains cause and effect without the real service; it is not evidence of a working production installation. Numbered screenshots in the user manual distinguish actual-app captures from demo captures.

## Files and sources of truth

| Actual package path | Maintainer role |
| --- | --- |
| [projects-host/image-review/public](../projects-host/image-review/public) | Review UI |
| [projects-host/host/image_review.py](../projects-host/host/image_review.py) | Revision-checked persistence and learning |
| [projects-host/image-review/tests](../projects-host/image-review/tests) | Synthetic fixture/backend/browser checks |
| [demo-source](../demo-source) | Editable demo HTML/CSS/runtime and embedded screenshot tour |
| [SOURCE-MANIFEST.json](../SOURCE-MANIFEST.json) | Original copied-source paths and SHA-256 checkpoint values |

The original working source is under C:/Users/lamon/Desktop/AI TOOLS/NAS for NAS modules; adjacent CAD/watch source locations are recorded by the full backup’s reviewed source manifest. This package contains only the explicitly copied source, not an automatic mirror. The main private nas-projects backup retains the broader shared host context.

## Setup, run and tests

Run commands from this repository root unless a `cd` is shown. Use a disposable checkout and fictional data for first setup. Dependencies, SDKs, signing material and personal data are not bundled. The following are continuation instructions grounded in the retained source, **not commands executed or newly certified by this handover**.

The real app requires the owner-authenticated Projects gateway. demo.html uses generated sample shapes.

Selected project check:

```powershell
python -B projects-host/image-review/tests/test_review.py
```

For the documentation demo alone, serve this repository on loopback with `python -m http.server 8765 --bind 127.0.0.1` and open `/demo.html`. Choose a free port if another preview is running. JavaScript syntax can be checked with `node --check demo-source/runtime.js`. `python demo-source/rebuild.py` rewrites demo.html, so run it only in a disposable checkout or an authorised demo-editing session. A local server cannot provide missing HA/CAD/NAS functions. Inspect browser tests for installed dependencies, fixture requirements and network targets before running them with the approved browser tooling.

## Data, configuration and backup boundaries

Documented runtime: /srv/data/image-review/decisions.sqlite3 and its previews/ sibling. Back up a consistent database plus catalog/previews/original media mappings; Git contains none of the private images, names or labels. Do not import production photos into demo fixtures.

Images/previews, names, labels and histories are private NAS data and are not included in this source repository. The demo uses generated sample shapes. Exported histories can contain sensitive annotations and should remain private unless reviewed.

Git preserves reviewed source and documentation. It does not copy browser storage, application databases, uploaded models/photos, accepted device settings, SDKs or credentials. Maintain independent recovery copies of the data identified above, including matching configuration and asset versions. Never add real secrets to examples, issues or logs. Private source copies on GitHub are not proof of a complete NAS/offsite data backup.

## Current verification and Git state

Before these documentation edits on 14 October 2026, this package was clean on branch `main` at `cce96e338b77b0361dbf6c897e1afb9b14962ab9` and its private upload was verified. All 17 manifest-listed source entries matched their stored checksums before editing. The upload follow-up has completed all 17 repositories and is paused; it does not run this tool or back up its live data.

These handover pages and README links accompany the private source package. Preserve them when continuing; stage only reviewed changes. Recheck current `git status --short --branch` and `git diff` before starting. No project-specific background schedule was inspected or changed in this documentation pass. Any service schedules in older notes are historical claims to verify in the actual deployment.

Earlier package checks and limits are recorded in [VALIDATION.md](../VALIDATION.md). This handover adds documentation/link/whitespace/secret and source-preservation checks only. No current NAS release, real hardware state, fresh installation, complete data restoration or offsite-backup freshness was verified here.

## Recovery approach

1. Preserve the current installation/data before changing it. Identify the exact code commit and data snapshot required; do not assume this package matches the running service.
2. Recover source into a new folder. Verify the source manifest and restore the project-specific configuration/assets described above separately. Recreate dependencies from the retained project files and guides.
3. Restore user data into an isolated instance or clean test browser. Check a representative editable record, associated files and save/reload behaviour, then compare to the original. Do not test recovery by overwriting production.
4. Record what actually restored and what remains missing. A demo opening or a passing syntax check is not a production recovery drill. Real deployment/device actions need the existing authorised workflow.

## Known limits and next work

The app depends on the owner-authenticated gateway and persistent database. No private photographs are used in the shareable demo. No new classifier or private-image scan is run by this documentation work.

**Priority:** Verify revision conflict/retry and per-pass undo with synthetic media. Keep gateway access owner-only. Learning calibrates the existing score cutoff; its retained holdout/near-duplicate limitations do not support claims of general classifier accuracy.

Common symptoms to check for this tool:

- Image missing: verify preview availability and do not blindly label it.
- Decision not saved: inspect retry/conflict state and connection.
- Learning inactive: reviewed labels or quality criteria may not be sufficient; manual review still works.

Keep [the release checklist](../RELEASE-CHECKLIST.md) and [third-party notes](../THIRD-PARTY.md) with the package. Original contributions use MIT; bundled/upstream code and assets keep their own licences. Public publication is a separate decision; preparing documentation is not permission to publish.
