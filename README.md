# self Forsquare Bot
Swarm の通知が X(Twitter) に連携されないため、自分でなんちゃって連携通知をします。  
webhook 用のサーバを立てる場所もアドレスもなかったので、crontab 等でポーリングすることで連携通知する仕組みです。

```
$ crontab -l
*/1 * * * * . ~/path/to/self_forsquare_bot/env; python main.py
```

```
$ cat ~/path/to/self_forsquare_bot/env
export CONSUMER_KEY=""
export CONSUMER_SECRET=""
export ACCESS_TOKEN=""
export ACCESS_SECRET=""
export BEARER_TOKERN=""
export FORSQUARE_ACCESS_TOKEN=""
```
