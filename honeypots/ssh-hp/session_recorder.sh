#!/usr/bin/env bash
LOGDIR="/var/log/tty"
USER=$(whoami)
TIMESTAMP=$(date +%Y%m%dT%H%M%S)
PID=$$
CLIENT_IP_RAW=$(echo "$SSH_CONNECTION" | awk '{print $1}')
CLIENT_IP=${CLIENT_IP_RAW//./-}
SESSION_BASE="${CLIENT_IP}_${USER}_${TIMESTAMP}_${PID}"

META_FILE="$LOGDIR/${SESSION_BASE}.meta.json"
TS_FILE="$LOGDIR/${SESSION_BASE}.typescript"
TM_FILE="$TS_FILE.timing"

mkdir -p "$LOGDIR"

cat <<EOF >"$META_FILE"
{
  "session_id":"$SESSION_BASE",
  "user":"$USER",
  "source_ip":"$CLIENT_IP_RAW",
  "start_time":"$(date --rfc-3339=seconds)"
}
EOF

exec /usr/bin/script -q -f --timing="$TM_FILE" "$TS_FILE" /bin/bash
