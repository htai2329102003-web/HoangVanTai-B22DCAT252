#!/bin/bash
# Open the same URL from the victim container; its source IP receives a 302 to the local simulation.
URL="http://10.0.0.100:8080/"
for i in $(seq 1 45); do
    if (echo > /dev/tcp/10.0.0.100/8080) >/dev/null 2>&1; then
        break
    fi
    sleep 1
done
firefox --new-window "$URL" >/tmp/url-cloaking-browser.log 2>&1 &
