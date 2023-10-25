# self Forsquare Bot
This is server/script programs to post Swarm notifications to X (Twitter) and mastdon.  

The following env file is required to run this program.
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
Script with polling method to run in crontab

```
$ crontab -l
*/1 * * * * bash /path/to/polling.sh
```

## server.py
A server-based program that receives and operates on webhooks.  
To receive a webhook, the server must provide an FQDN and SSL certification.
```
$ nohup python server.py &
```