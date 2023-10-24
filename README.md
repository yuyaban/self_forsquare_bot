# self Forsquare Bot
Swarm の通知が X(Twitter) に連携されないため、自分でなんちゃって連携通知をします。  
必要な環境変数は以下の通りです。
```
$ cat ~/path/to/self_forsquare_bot/env
export CONSUMER_KEY=""
export CONSUMER_SECRET=""
export ACCESS_TOKEN=""
export ACCESS_SECRET=""
export BEARER_TOKERN=""
export FORSQUARE_ACCESS_TOKEN=""
export MASTDN_CLIENT_KEY=""
export MASTDN_CLIENT_SECRET=""
export MASTDN_ACCESS_TOKEN=""
```

## main.py
webhook 用のサーバを立てる場所もアドレスもなかったので、crontab 等でポーリングすることで連携通知する仕組みです。

```
$ crontab -l
*/1 * * * * . ~/path/to/self_forsquare_bot/env; python main.py
```

## server.py
FQDN を用意して、Webhook を受け取るサーバを用意できるならこちらを使うほうが良い
```
$ python server.py
```