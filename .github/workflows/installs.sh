#/bin/bash
# helper script to install this repo's packages/dependencies (optionally in dev/edit mode).

set -e

SCRIPT_DIR="$(realpath "$(dirname "$0")")"
ROOT_DIR="$(realpath "$SCRIPT_DIR/../..")"

function main() {
    cd "$ROOT_DIR"

    edit=()
    DEV=""

    # TODO: support long form options like --import
    while getopts "ed" arg; do
        case $arg in
            e)
                edit=(-e)
                echo "installing packages in edit mode!"
                ;;
            d)
                echo "installing dev dependencies!"
                DEV="[dev]"
                ;;
            h)
                usage
                exit
                ;;
        esac
    done

    echo -e "\nstarting installations..."
    pip install "${edit[@]}" ./serialization$DEV
    pip install "${edit[@]}" ./actor_controller$DEV
    pip install "${edit[@]}" ./rpi_controller$DEV
    pip install "${edit[@]}" ./core$DEV
    pip install "${edit[@]}" ./standard_resources$DEV
    pip install "${edit[@]}" ./runners/mujoco$DEV
    sudo apt install -y libcereal-dev
    pip install "${edit[@]}" ./genotypes/cppnwin$DEV
    echo "install.sh complete!"
}

function usage() {
    echo -e "Helper script for installing dependencies."
    echo -e "\nUSAGE:"
    echo -e "\tinstalls.sh [-e] [-d] [-h]\n"
    echo -e "\tinstalls.sh -e    # install packages in edit mode (can be combined with -d)"
    echo -e "\tinstalls.sh -d    # install dev dependencies as well (can be combined with -e)"
    echo -e "\tinstalls.sh -h    # display this help and exit"
}

main "$@"