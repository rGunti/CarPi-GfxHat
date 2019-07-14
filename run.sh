#!/usr/bin/env bash

SCRIPT_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${SCRIPT_LOCATION}

sleep 2
/usr/bin/python3 ./main.py
