# Marlin Firmware Builder

Build firmware from the [Marlin](https://github.com/MarlinFirmware/Marlin) **`bugfix-2.1.x`** branch
for any of its [example configurations](https://github.com/MarlinFirmware/Configurations/tree/bugfix-2.1.x/config/examples),
without installing a build environment.

Only `bugfix-2.1.x` is built, always from its latest commit. Release versions of Marlin are not available here.

**You need a free [GitHub account](https://github.com/signup) to request a build**, because
each request is a GitHub issue and the download link is posted as a reply to it.

**[Open the configuration picker](https://ellensp.github.io/MarlinWebBuild/)**

1. Sign in to GitHub, then find your printer and pick a build environment.
2. Click **Request build on GitHub** and submit the pre-filled issue.
3. A few minutes later the issue gets a reply with a download link.

Downloads are kept for about two weeks. `bugfix-2.1.x` has the latest fixes and is often more stable than the last release, but it changes daily and recent changes can introduce new bugs.

## How it works

| Piece | What it does |
|---|---|
| `site/` | Static picker page, deployed to GitHub Pages |
| `.github/workflows/pages.yml` | Every 6 hours, indexes all example configs and their PlatformIO envs, then redeploys the page |
| `.github/ISSUE_TEMPLATE/build.yml` | Issue form the picker pre-fills (`?config=…&env=…`) |
| `.github/workflows/build.yml` | On a `build-request` issue: validate, build with PlatformIO, upload a zip to the `builds` release, reply and close |
| `.github/workflows/prune.yml` | Daily: delete release assets older than 14 days, lock old requests |
| `tools/marlin_index.py` | Maps example configs to envs, using the same `pins.h` lookup as Marlin's `mfenvs` |
| `tools/parse_request.py` | Parses and validates the issue form text |

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

```sh
git clone --depth 1 --filter=blob:none --sparse -b bugfix-2.1.x https://github.com/MarlinFirmware/Marlin _marlin
git -C _marlin sparse-checkout set Marlin/src/pins
git clone --depth 1 --filter=blob:none --sparse -b bugfix-2.1.x https://github.com/MarlinFirmware/Configurations _cfg
git -C _cfg sparse-checkout set --no-cone '/config/examples/**/Configuration.h'
python3 tools/marlin_index.py index _marlin _cfg | jq '{repo:"you/MarlinWebBuild",branch:"bugfix-2.1.x",marlin:"",configs:"",generated:"",items:.}' > site/index.json
python3 -m http.server -d site
```
