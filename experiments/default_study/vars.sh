#!/bin/bash
# this file defines variables that can be sourced by other shell scripts
# (don't put any code here, just variables)

SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exppath="$SCRIPT_DIR" # path of experiment directory

study="$(basename "$(realpath "$SCRIPT_DIR")")" # e.g. "default_study"
# base path at which to store any experiments for this user:
mainpath="/storage/$USER"
# path to this particular experiment:
studypath="${mainpath}/${study}"