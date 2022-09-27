#!/bin/bash
set -e

SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/vars.sh" # read variables

function main () {
    mkdir "${studypath}"
    # start a screen session running setup-experiments.sh
    screen -d -m -S run_loop -L -Logfile "${studypath}/setuploop.log" "${SCRIPT_DIR}/setup-experiments.sh"
}

main "$@"