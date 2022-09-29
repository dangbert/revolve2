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


experiments=("defaultexperiment")
seasons_conditions=("1.0_1.0_0")
runs=10
num_generations="100"
num_terminals=2 # DO NOT TOUCH

# gens for boxplots and snapshots
generations=(100)
# these params are the same for all exps
# gens for boxplots and snapshots
generations=(100)
#gen for lineplots
final_gen=100
runs=10