# Discord Webhook for Custom GeoGuessr Daily Challenges

<div align="center">

[![GitHub License](https://img.shields.io/github/license/d1s4rr4y/Discord-Webhook?style=for-the-badge)](https://github.com/d1s4rr4y/Discord-Webhook/blob/master/LICENSE)
![GitHub Release](https://img.shields.io/github/v/release/d1s4rr4y/Discord-Webhook?style=for-the-badge)

![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Python](https://img.shields.io/badge/python-%233670A0.svg?style=for-the-badge&logo=python&logoColor=ffdd54)
![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)

</div>

Creates a GeoGuessr challenge link on a schedule (according to some pre-defined rules), and sends that to a discord channel via webhooks.

**Note:** Usage of this script requires a GeoGuessr account and an active Geoguessr subscription.

## Setup

To make this work, you'll need 3 secrets defined in your repository:

- `NCFA_TOKEN`
- `MAP_ID`
- `WEBHOOK_URL`

Optionally, add a `ROLE_ID` repository secret to ping a Discord role when the challenge is posted. If it is unset, no role will be pinged.

Secrets can be set in **Settings > Secrets and Variables > Actions**. Make sure to set these as **Repository Secrets**, NOT Environment Secrets.

`WEBHOOK_URL` is created as standard through Discord, for instructions on how to create a webhook see Discord's own guide [here](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)

`MAP_ID` is simply the string of characters at the end of a map link. For example, the link t "An Arbitrary World" is `https://www.geoguessr.com/maps/6089bfcff6a0770001f645dd`, so you would set `MAP_ID` to `6089bfcff6a0770001f645dd`

`NCFA_TOKEN` is more involved:

1. Log into GeoGuessr in your browser of choice.
2. Open Dev tools (`F12` or `CTRL/CMD + SHIFT + I`)
3. Navigate to **Application** (Chrome/Edge) or **Storage** (Firefox)
4. Expand **Cookies**, and select `https://geoguessr.com`
5. Find the cookie value named `_ncfa` and copy its value. Use this as the value for `NCFA_TOKEN`

**NOTE:** Do not share this NCFA cookie value with anyone, **it will grant access to your GeoGuessr account.**

## Local Testing

Run the unit tests from the repository root with Python 3.11 or newer:

```shell
python -m pip install requests
python -m unittest discover --start-directory tests --verbose
```

The tests use mocks for external requests, so they do not require GeoGuessr credentials or a Discord webhook URL.

## Changing Settings

### Message Schedule

In `.github/workflows/daily.yml`, there is the following block:

```yaml
on:
  workflow_dispatch:
```

This allows the workflow to be run manually, either through the built-in GitHub Actions menu, or via the GitHub API.

To schedule the workflow, you can add

```yaml
schedule:
  - cron: "0 12 * * *"
```

under `on:`, alongside `workflow_dispatch`. `cron` is defined in the standard cron format, i.e. `minute hour day month weekday`.
The example above schedules the workflow for 12:00 UTC (noon) every day.
For a graphical cron schedule expression editor, use [crontab guru](https://crontab.guru/)

Scheduling workflows through GitHub Actions often leads to hugely delayed workflows, and so it is also possible to schedule this workflow using services such as [Cron Job](https://console.cron-job.org/jobs), CloudFlare, or AWS, and the [GitHub REST API](https://docs.github.com/en/rest?apiVersion=2026-03-10)

### Challenge Settings

When optional challenge settings are omitted or empty, these defaults are used:

- `TIME_LIMIT`: `90` seconds (`0` means unlimited)
- `FORBID_MOVING`: `false`
- `FORBID_ZOOMING`: `false`
- `FORBID_ROTATING`: `false`

To override these defaults in GitHub Actions, add the corresponding values as repository variables under **Settings > Secrets and variables > Actions > Variables**. Boolean values must be `true` or `false`.
