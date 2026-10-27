#!/bin/bash
# Open the same URL from the scanner container; its source IP should receive HTTP 200.
URL="http://192.168.1.100:8080/"
for i in $(seq 1 45); do
    if (echo > /dev/tcp/192.168.1.100/8080) >/dev/null 2>&1; then
        break
    fi
    sleep 1
done
firefox --new-window "$URL" >/tmp/url-cloaking-browser.log 2>&1 &
