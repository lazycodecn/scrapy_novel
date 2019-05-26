#!/usr/bin/env bash
#!/usr/bin/tail
#!/usr/sbin/cron
#!/usr/sbin/service

service cron start
crontab /novel/root >> /novel/novel.log 2>&1
tail -f  /novel/novel.log

exec "$@"