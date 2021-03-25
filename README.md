# Minecraft (VimeWorld) log analyzer

It looks at Minecraft (VimeWorld) log file, retrieves bosses and time when they was killed. And it sends a notification into Discord channel if there are updates.


## Installation

```sh
git clone https://github.com/rantanevich/minecraft-log-scraper.git
cd minecraft-log-scraper
pip install -r requirements.txt
```


## Usage

You should create environment variables:

| Variable                | Required | Example                                                                               |
|-------------------------|----------|---------------------------------------------------------------------------------------|
| MINECRAFT_LOG_FILE      | yes      | `%AppData%\.vimeworld\minigames\logs\latest.log`                                      |
| DISCORD_WEBHOOK_ALERT   | yes      | `https://discord.com/api/webhooks/{webhook.id}/{webhook.token}`                       |
| DISCORD_WEBHOOK_RESPAWN | yes      | `https://discord.com/api/webhooks/{webhook.id}/{webhook.token}/messages/{message.id}` |

There are two variables that you can change for your purposes in the script:

| Variable        | Default | Comments                                                                  |
|-----------------|---------|---------------------------------------------------------------------------|
| UPDATE_TIMEOUT  | `5m`    | How often the log file will be read                                       |
| ALERT_THRESHOLD | `3m`    | If there're bosses that respawns in less than this time, you'll get alert |

After all settings you only need to run the script:
```sh
python main.py
```

## References

* [Discord. Webhook API](https://discord.com/developers/docs/resources/webhook)
* [Discord. Intro to Webhooks](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)
