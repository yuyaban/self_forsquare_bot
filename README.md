# self Forsquare Bot
Swarm の通知が X(Twitter) に連携されないため、自分でなんちゃって連携通知をします。

```
$ crontab -l
*/1 * * * * . ~/path/to/self_forsquare_bot/env; python main.py
```

```
export CONSUMER_KEY=""
export CONSUMER_SECRET=""
export ACCESS_TOKEN=""
export ACCESS_SECRET=""
export BEARER_TOKERN=""
export FORSQUARE_ACCESS_TOKEN=""
```