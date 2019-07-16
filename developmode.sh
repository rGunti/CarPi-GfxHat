#!/usr/bin/env bash

SCRIPT_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${SCRIPT_LOCATION}

if [[ ! -f "/etc/systemd/system/multi-user.target.wants/carpi-display.service" ]]; then
    sleep 5
    echo "[i] Running Dev Mode app"
    /usr/bin/python3 ./developmode.py
fi
