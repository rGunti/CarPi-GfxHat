#!/usr/bin/env bash

# ### Help ###############################################################
function printHelp {
cat << EOF
Usage: develop.sh [<Parameters>]

Parameters:
    -e / --enable
        Enable development mode
    -d / --disable
        Disable development mode
EOF
}

# ### Arguments ##########################################################
SCRIPT_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
POSITIONAL=()
while [[ $# -gt 0 ]]
do
    key="$1"

    case ${key} in
        -e|--enable)
        OPT_RESPONSE=E
        shift
        ;;
        -d|--disable)
        OPT_RESPONSE=D
        shift
        ;;
        -h|--help)
        printHelp
        exit 0
        shift
        ;;
        *)
        POSITIONAL+=("$1")
        shift
        ;;
    esac
done

# ### Script #############################################################

function disableService {
    SERVICE=$1
    echo "[*] Disabling $SERVICE ..."
    systemctl stop ${SERVICE}
    systemctl disable ${SERVICE}
}

function enableService {
    SERVICE=$1
    echo "[*] Enabling $SERVICE ..."
    systemctl start ${SERVICE}
    systemctl enable ${SERVICE}
}

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

cat << EOF
 ========== CarPi GfxHat Developer Mode ==========
This script will enable the Developer Mode of the
CarPi GfxHat Display software. This will do the
following:

- Shutdown and disable the CarPi GfxHat Display Daemon
- Shutdown and disable the CarPi OBD Daemon

EOF

if [[ -z ${OPT_RESPONSE} ]]; then
    echo -n "[?] Choose the action to continue: [Enable/Disable/Quit] "
    read -n 1 action
    echo ""
else
    action=${OPT_RESPONSE}
fi

case ${action} in
[Ee])
    echo "[*] Enabling CarPi GfxHat Developer Mode ..."
    disableService carpi-display
    disableService carpi-obd-daemon
    echo "[*] Showing Information on Display"
    cd ${SCRIPT_LOCATION}
    /usr/bin/python3 ./developmode.py > /dev/null &
    echo "[O] Operation completed!"
    ;;
[Dd])
    echo "[*] Disabling CarPi GfxHat Developer Mode ..."
    enableService carpi-display
    enableService carpi-obd-daemon
    echo "[O] Operation completed!"
    ;;
*)
    echo "[*] Quitting script ..."
    ;;
esac

echo " =========== Script has ended =========== "
