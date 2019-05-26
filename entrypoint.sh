#!/usr/bin/env bash
#!/usr/bin/tail
#!/usr/sbin/cron
#!/usr/sbin/service

tail -f  /novel/novel.log
service cron start
crontab /novel/root >> /novel/novel.log 2>&1

exec "$@"