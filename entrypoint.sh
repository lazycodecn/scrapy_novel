#!/usr/bin/env bash
#!/usr/bin/tail
#!/usr/sbin/cron
#!/usr/sbin/service

service cron restart
exec "$@"
tail -f  /novel/novel.log

