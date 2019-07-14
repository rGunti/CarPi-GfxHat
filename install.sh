#!/usr/bin/env bash

# ### Help ###############################################################
function printHelp {
cat << EOF
Usage: install.sh [<Parameters>]

Parameters:
    -l / --accept-license
        Auto-accepts the license agreement
    -d / --skip-dependencies
        Skips dependency checking
    -s / --skip-install-daemon
        Skips the daemon installation
    -D / --install-daemon
        Auto-accepts daemon installation
    -r / --restart-daemon
        Restarts the daemon after installation (requires daemon to be installed)

    -F / --fast-install
        Runs a fast install:
            - Accept license
            - Skip dependency checking
            - Skip daemon installation
EOF
}

# ### Arguments ##########################################################
POSITIONAL=()
while [[ $# -gt 0 ]]
do
    key="$1"

    case ${key} in
        -l|--accept-license)
        OPT_ACCEPT_LICENSE=1
        shift
        ;;
        -d|--skip-dependencies)
        OPT_SKIP_DEPENDENCIES=1
        shift
        ;;
        -s|--skip-install-daemon)
        OPT_SKIP_INSTALL_DAEMON=1
        shift
        ;;
        -D|-install-daemon)
        OPT_INSTALL_DAEMON=1
        shift
        ;;
        -r|--restart-daemon)
        OPT_RESTART_DAEMON=1
        shift
        ;;
        -F|--fast-install)
        OPT_ACCEPT_LICENSE=1
        OPT_SKIP_DEPENDENCIES=1
        OPT_SKIP_INSTALL_DAEMON=1
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

function copyFile {
    DESTINATION=$1
    SOURCE=$2

    echo "    Copying $(basename "$SOURCE") ..."
    cp -f "$SOURCE" "$DESTINATION"
}

function copyDir {
    DESTINATION=$1
    SOURCE=$2

    echo "    Copying $(basename "$SOURCE") ..."
    cp -f -R "$SOURCE" "$DESTINATION"
}

SCRIPT_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

INSTALL_SOURCE="$SCRIPT_LOCATION/"
INSTALL_DESTINATION="/usr/bin/carpi-ui/"
CONFIG_DESTINATION="/etc/carpi/"
CONFIG_FILE_DESTINATION="/etc/carpi/ui.conf"

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

cat << EOF
 ========== CarPi GfxHat Installer ==========
This script install the following apps:
 - CarPi GfxHat UI

Any existing installations will be replaced though configuration files will be left
alone. You will receive an updated template configuration.

The installation will take place in the following directory:
$INSTALL_DESTINATION

EOF

if [[ ${OPT_ACCEPT_LICENSE} -ne 1 ]]
then
    cat << EOF
This software is distributed under the MIT License:

    Copyright (c) 2019 Raphael "rGunti" Guntersweiler

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
EOF

    echo -n "[?] Do you accept this license? [Y/N] "
    read -n 1 license_agree
    echo ""

    case ${license_agree} in
    [Yy])
        echo "[*] Please wait while the installation starts ..."
        ;;
    *)
        echo "[*] Quitting installer ..."
        echo " =========== Script has ended =========== "
        exit 1
        ;;
    esac
else
    echo "[i] License accepted (as requested by -l / --accept-license)"
fi

if [[ ${OPT_SKIP_DEPENDENCIES} -ne 1 ]]; then
    echo "[*] Installing dependencies ..."
    /usr/bin/pip3 install -r "$INSTALL_SOURCE/requirements.txt"
else
    echo "[i] Skipped dependency checks (as requested by -d / --skip-dependencies)"
fi

if [[ ! -d "$INSTALL_DESTINATION" ]]; then
    echo "[*] Creating destination directory ..."
    mkdir -p "$INSTALL_DESTINATION"
fi

echo "[*] Installing Framework ..."
copyDir "$INSTALL_DESTINATION" "$INSTALL_SOURCE/lib"
copyDir "$INSTALL_DESTINATION" "$INSTALL_SOURCE/obd"

echo "[*] Installing Software ..."
copyDir "$INSTALL_DESTINATION" "$INSTALL_SOURCE/app"
copyDir "$INSTALL_DESTINATION" "$INSTALL_SOURCE/utils"
copyFile "$INSTALL_DESTINATION" "$INSTALL_SOURCE/main.py"
copyFile "$INSTALL_DESTINATION" "$INSTALL_SOURCE/run.sh"
copyFile "$INSTALL_DESTINATION" "$INSTALL_SOURCE/develop.sh"

echo "[*] Installing Resources ..."
copyDir "$INSTALL_DESTINATION" "$INSTALL_SOURCE/fonts"

echo "[*] Running post-install configuration ..."
chmod +x "$INSTALL_DESTINATION/main.py"
chmod +x "$INSTALL_DESTINATION/run.sh"
chmod +x "$INSTALL_DESTINATION/develop.sh"

echo "[*] Checking for configuration files ..."
if [[ ! -d "$CONFIG_DESTINATION" ]]; then
    echo "[*] Creating Configuration directory ..."
    mkdir -p "$CONFIG_DESTINATION"
fi
if [[ ! -f "$CONFIG_FILE_DESTINATION" ]]; then
    copyFile "$CONFIG_DESTINATION" "$INSTALL_SOURCE/ui.conf"
else
    copyFile "$CONFIG_FILE_DESTINATION.template" "$INSTALL_SOURCE/ui.conf"
fi

echo ""
echo "[O] Installation has been completed!"

if [[ ${OPT_SKIP_INSTALL_DAEMON} -ne 1 ]]; then
    if [[ ${OPT_INSTALL_DAEMON} -ne 1 ]]; then
        echo -n "[?] Do you want to setup this app as a service (daemon)? [Y/N] "
        read -n 1 daemon_setup
        echo ""
    else
        daemon_setup=Y
        echo "[i] Auto-installing daemon (as requested by -D / --install-daemon)"
    fi

    case ${daemon_setup} in
    [Yy])
        echo "[*] Setting up a Daemon for you ..."
        cat << EOF > /etc/systemd/system/carpi-display.service
[Unit]
Description=CarPi Display

[Service]
Type=simple
ExecStart=$INSTALL_DESTINATION/run.sh
WorkingDirectory=$INSTALL_DESTINATION
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
        systemctl daemon-reload
        systemctl enable carpi-display
        systemctl start carpi-display
        ;;
    esac
else
    echo "[i] Skipped installing daemon (as requested by -s / --skip-install-daemon)"
fi

if [[ ${OPT_RESTART_DAEMON} -eq 1 ]]; then
    echo "[*] Restarting Display daemon (as requested by -r / --restart-daemon)"
    systemctl restart carpi-display
fi

echo "[O] Installation has been completed successfully!"
echo " =========== Script has ended =========== "
