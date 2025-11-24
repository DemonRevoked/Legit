FROM debian:bullseye-slim

# Install the standard NTP daemon package
RUN apt-get update && \
    apt-get install -y ntp && \
    rm -rf /var/lib/apt/lists/*

# Copy our custom NTP configuration into the container
COPY ntp.conf /etc/ntp.conf

# The ntpd process, which runs as the 'ntp' user after starting, needs write
# access to these directories. /var/log/ntp is the volume mount point for logs.
RUN mkdir -p /var/lib/ntp /var/log/ntp && \
    chown -R ntp:ntp /var/lib/ntp /var/log/ntp

# Run ntpd in the foreground.
# -g: Allows large time adjustments at startup.
# -n: Prevents forking, keeping the process in the foreground for container management.
# The daemon starts as root to bind to the privileged NTP port (123),
# and we instruct it to continue running as root to avoid volume permission issues.
CMD ["ntpd", "-g", "-n", "-u", "root"]