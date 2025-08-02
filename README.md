# robogeorge

A little discord bot with some experimental functions.

Not intended for outside use. This is just here for my own use.

## Setup

- `cp .env.template .env`
- fill out `DISCORD_TOKEN` and `STEAM_API_TOKEN`
- have `python3` installed
- `tmux`
- `bash start.sh`
- ctrl-B, D to detach

## Always start up on machine boot

- Update `User` and `WorkingDirectory` in `robogeorge.service`

```shell
cp robogeorge.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable robogeorge.service
sudo systemctl start robogeorge.service
```

To check status: `sudo systemctl status robogeorge.service`

To view tmux session: `tmux attach -t robogeorge`
