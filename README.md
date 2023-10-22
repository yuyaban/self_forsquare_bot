# self Forsquare Bot
Swarm の通知が X(Twitter) に連携されないため、自分でなんちゃって連携通知をします。

```
$ crontab -l
*/1 * * * * . ~/path/to/self_forsquare_bot/env; python main.py
```