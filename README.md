# Discord Webhook for Custom GeoGuessr Daily Challenges

<div align="center">

[![GitHub License](https://img.shields.io/github/license/d1s4rr4y/Discord-Webhook?style=for-the-badge)](https://github.com/d1s4rr4y/Discord-Webhook/blob/master/LICENSE)
![GitHub Release](https://img.shields.io/github/v/release/d1s4rr4y/Discord-Webhook?style=for-the-badge)

![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Python](https://img.shields.io/badge/python-%233670A0.svg?style=for-the-badge&logo=python&logoColor=ffdd54)
![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)

</div>

Creates a GeoGuessr challenge and posts its link and settings to a Discord channel. It can be run manually or on a schedule with GitHub Actions.

You need a GeoGuessr account with an active subscription, a Discord webhook, and Python 3.11+ for local use.

## GitHub setup

In **Settings > Secrets and variables > Actions**, add these repository secrets:

| Secret        | Required | Purpose                                 |
| ------------- | -------- | --------------------------------------- |
| `NCFA_TOKEN`  | Yes      | Your GeoGuessr `_ncfa` cookie           |
| `WEBHOOK_URL` | Yes      | Discord channel webhook URL             |
| `MAP_ID`      | No       | Fixed map, overrides automatic rotation |
| `ROLE_ID`     | No       | Discord role to mention                 |

`NCFA_TOKEN` grants access to your GeoGuessr account. Keep it private and store it only as a GitHub secret. To find it, sign in to GeoGuessr, open your browser's developer tools, then find the `_ncfa` cookie under the site's cookies in **Application** (Chrome/Edge) or **Storage** (Firefox).

Create a Discord webhook in the destination channel's **Settings > Integrations > Webhooks**, then save its URL as `WEBHOOK_URL`. See [Discord's webhook guide](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) for details.

To run the workflow, open **Actions > GeoGuessr Daily Challenge** and choose **Run workflow**.

## Map selection

Set either `MAP_ID` or the `MAP_IDS` repository variable:

- `MAP_ID` selects one fixed map and takes precedence.
- `MAP_IDS` is an ordered, comma-separated list used for automatic rotation, for example `map-a,map-b,map-c`.
- Empty entries and surrounding whitespace in `MAP_IDS` are ignored.
- With no usable map ID, the run stops with a configuration error.

Automatic selection uses the UTC day number modulo the number of configured maps. This means reruns on the same UTC date choose the same map, and selection wraps around the list.

A map ID is the final part of a GeoGuessr map URL. For example, the ID in `https://www.geoguessr.com/maps/6089bfcff6a0770001f645dd` is `6089bfcff6a0770001f645dd`.

## Challenge settings

Add these as repository variables under **Settings > Secrets and variables > Actions > Variables**. Omitted or blank values use the defaults.

| Variable          | Default | Description                          |
| ----------------- | ------: | ------------------------------------ |
| `TIME_LIMIT`      |    `90` | Time in seconds; `0` means unlimited |
| `FORBID_MOVING`   | `false` | Prevent moving                       |
| `FORBID_ZOOMING`  | `false` | Prevent zooming                      |
| `FORBID_ROTATING` | `false` | Prevent panning                      |

Boolean values must be `true` or `false` (case-insensitive).

## Scheduling

The workflow currently supports manual runs. To schedule it, add a `schedule` entry alongside `workflow_dispatch` in `.github/workflows/daily.yml`:

```yaml
on:
  workflow_dispatch:
  schedule:
    - cron: "0 12 * * *"
```

This example runs daily at 12:00 UTC. Cron uses the standard `minute hour day-of-month month day-of-week` format. GitHub may delay scheduled workflows during busy periods.

It is also possible to instead schedule the workflow using the GitHub REST API and an alternative provider with cron scheduling,
to avoid GitHub's delays.

## Run locally

From the repository root, install the dependency:

```shell
python -m pip install requests
```

Set the required values in your shell, along with either `MAP_ID` or `MAP_IDS`, then run:

```shell
python daily_challenge.py
```

For example, in PowerShell:

```powershell
$env:NCFA_TOKEN = "your-ncfa-token"
$env:WEBHOOK_URL = "your-discord-webhook-url"
$env:MAP_IDS = "map-a,map-b,map-c"
python daily_challenge.py
```

Optional settings such as `TIME_LIMIT` and `ROLE_ID` can also be supplied as environment variables.

## Tests

Run the unit tests from the repository root:

```shell
python -m unittest discover --start-directory tests --verbose
```

Tests mock external requests, so they do not need credentials and will not create challenges or send Discord messages.
