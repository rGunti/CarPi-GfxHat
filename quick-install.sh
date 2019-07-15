#!/usr/bin/env bash

cat << EOF
================================================================

 ██████╗ █████╗ ██████╗ ██████╗ ██╗     ██████╗ ███████╗██╗  ██╗
██╔════╝██╔══██╗██╔══██╗██╔══██╗██║    ██╔════╝ ██╔════╝╚██╗██╔╝
██║     ███████║██████╔╝██████╔╝██║    ██║  ███╗█████╗   ╚███╔╝
██║     ██╔══██║██╔══██╗██╔═══╝ ██║    ██║   ██║██╔══╝   ██╔██╗
╚██████╗██║  ██║██║  ██║██║     ██║    ╚██████╔╝██║     ██╔╝ ██╗
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝     ╚═════╝ ╚═╝     ╚═╝  ╚═╝

================= CARPI GFX QUICK INSTALLER ====================

EOF

# ### Base ################################################
function logProcess {
    echo "[*] $1"
}
function logVerbose {
    echo "    $1"
}
function logInfo {
    echo "[i] $1"
}
function logQuestion {
    echo -n "[?] $1 "
}
function logWarn {
    echo "[!] $1"
}
function logError {
    echo "[x] $1"
}

function stop {
    EXIT_CODE=$1
    if [[ ${EXIT_CODE} -ne 0 ]]; then
        echo "=================== [x] Script has ended [x] ==================="
        exit ${EXIT_CODE}
    else
        echo "=================== [i] Script has ended [i] ==================="
        exit 0
    fi
}

function checkForRoot {
    if [[ $EUID -ne 0 ]]; then
        logError "Script must be started using sudo / root"
        stop 1
    fi
}

# ### Configuration #######################################
REPO_URL=https://github.com/rGunti/CarPi-GfxHat.git
REPO_CHECKOUT=/tmp/carpi-install
REQUIRE_ROOT=1

# ### Arguments ###########################################
POSITIONAL=()
while [[ $# -gt 0 ]]; do
    key="$1"

    case ${key} in
        --keep-source)
        OPT_KEEP_SOURCE=1
        shift
        ;;
        *)
        POSITIONAL+=("$1")
        shift
        ;;
    esac
done

# ### Script ##############################################
SCRIPT_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [[ ${REQUIRE_ROOT} -eq 1 ]]; then
    checkForRoot
fi

if [[ -d ${REPO_CHECKOUT} ]]; then
    logInfo "Checkout directory $REPO_CHECKOUT already exists"
    logProcess "Cleaning up checkout directory ..."
    rm -rf ${REPO_CHECKOUT}
fi

logProcess "Cloning repository ..."
git clone ${REPO_URL} ${REPO_CHECKOUT}
cd ${REPO_CHECKOUT}

logProcess "Installing software ..."
bash install.sh --fast-install

cd ${SCRIPT_LOCATION}
logInfo "Installation completed!"

if [[ ${OPT_KEEP_SOURCE} -ne 1 ]]; then
    logProcess "Cleaning up ..."
    rm -rf ${REPO_CHECKOUT}
    logInfo "Cleanup completed"
else
    logInfo "Source has not been cleaned up"
    logVerbose "You can find it here: $REPO_CHECKOUT"
fi

# ### End-Of-Script #######################################
stop