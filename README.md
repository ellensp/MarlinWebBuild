# Marlin Firmware Builder

Build [Marlin](https://github.com/MarlinFirmware/Marlin) firmware for any of its
[example configurations](https://github.com/MarlinFirmware/Configurations/tree/bugfix-2.1.x/config/examples),
without installing a build environment.

You can build **`bugfix-2.1.x`** (always from its latest commit) or any Marlin release with a `latest-*` tag
(`latest-2.1.x`, `latest-2.1.1`, `latest-2.1.0`, `latest-2.0.x`, ...). A release is built with the example
configurations of the same version.

**You need a free [GitHub account](https://github.com/signup) to request a build**, because
each request is a GitHub issue and the download link is posted as a reply to it.

**[Open the configuration picker](https://ellensp.github.io/MarlinWebBuild/)**

1. Sign in to GitHub, choose a Marlin version, then find your printer and pick a build environment.
2. Click **Request build on GitHub** and submit the pre-filled issue.
3. A few minutes later the issue gets a reply with a download link.

Downloads are kept for about two weeks. `bugfix-2.1.x` has the latest fixes and is often more stable than the last release, but it changes daily and recent changes can introduce new bugs. A release doesn't have the fixes made since it came out.

## How it works

| Piece | What it does |
|---|---|
| `site/` | Static picker page, deployed to GitHub Pages |
| `.github/workflows/pages.yml` | Every 6 hours, indexes the example configs and their PlatformIO envs for each Marlin version, then redeploys the page |
| `.github/ISSUE_TEMPLATE/build.yml` | Issue form the picker pre-fills (`?version=…&config=…&env=…`) |
| `.github/workflows/build.yml` | On a `build-request` issue: validate, build with PlatformIO, upload a zip to the `builds` release, reply and close |
| `.github/workflows/prune.yml` | Daily: delete release assets older than 14 days, lock old requests |
| `tools/marlin_versions.py` | Lists the Marlin versions (`bugfix-2.1.x` and the `latest-*` tags) and the Configurations ref for each |
| `tools/marlin_index.py` | Maps example configs to envs, using the same `pins.h` lookup as Marlin's `mfenvs` |
| `tools/parse_request.py` | Parses and validates the issue form text |

Each `latest-*` tag is offered as the release it points to (`latest-2.1.x` → `2.1.2.9`), and tags on the same commit are listed once.
The examples come from the Configurations tag of the same version, else its `release-<version>` branch, else the nearest shorter
version (Marlin `2.1.0.5` uses Configurations `2.1`).

A build for the same Marlin commit, configuration folder and env is reused rather than rebuilt.
Users are limited to `DAILY_LIMIT` requests per day (see `build.yml`); the repo owner is exempt.

## Setting up your own copy

1. Push this repo to GitHub as a **public** repository (Actions minutes are free for public repos).
2. **Settings → Pages → Build and deployment → Source:** GitHub Actions.
3. **Issues → Labels → New label:** `build-request`. The issue form applies it, and the build workflow only runs on issues with it.
4. **Actions → Pages → Run workflow** to publish the picker for the first time.
5. If you renamed the repo or it's under another account, update the picker URL in `README.md` and
   `.github/ISSUE_TEMPLATE/build.yml` / `config.yml`.

## Testing locally

Build the version list and one index per version as the Pages workflow does, then serve the page:

```sh
python3 tools/marlin_versions.py list > versions.json
# For each version: sparse-clone Marlin at marlin_ref and Configurations at configs_ref, then
python3 tools/marlin_index.py index _marlin _cfg > site/index/<id>.json
# and write site/versions.json ({repo, generated, versions: [...]}); see the "Build indexes" step in pages.yml
python3 -m http.server -d site
```
