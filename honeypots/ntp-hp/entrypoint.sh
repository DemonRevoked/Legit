#!/bin/bash

echo "[INFO] Starting NTP honeypot..."

# Ensure the log directory exists and is owned by the 'ntp' user.
# The 'ntpd' process runs as 'ntp' and needs write permissions here.
# Using -R for recursive chown to ensure existing files also have correct ownership.
mkdir -p /var/log/ntp # Ensure directory exists
chown -R ntp:ntp /var/log/ntp # Set ownership for the ntp user
chmod -R u+rwX,g+rwX,o+rwX /var/log/ntp
echo "[INFO] Set ownership of /var/log/ntp and its contents for user 'ntp'."

# Run ntpd in foreground with unprivileged user
exec ntpd -n -c /etc/ntpd.conf
