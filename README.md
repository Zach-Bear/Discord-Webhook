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

## Changing Settings
### Message Schedule
In `.github/workflows/daily.yml`, there is the following block:

```yml
on:
  schedule:
    - cron: "0 12 * * *"
```

This defines a standard cron format scheduler, i.e. `minute hour day month weekday`. Edit this line to change when the message is scheduled for (by default, it is noon UTC, every day). 
For a graphical cron schedule expression editor, use [crontab guru](https://crontab.guru/)

### Challenge Settings
In `daily_challenge.py` there is a section containing the following: 

```py
payload = {
    "map": MAP_ID,
    "forbidMoving": False,
    "forbidZooming": False,
    "forbidRotating": False,
    "timeLimit": 120
}
```

`forbidMoving`, `forbidZooming`, `forbidRotating`, and `timeLimit` can be changed to set the challenge settings. `timeLimit` is defined in seconds, and setting it equal to `0` will create a challenge with no time limit.
