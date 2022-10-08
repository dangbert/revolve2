#!/bin/bash
# this file defines variables that can be sourced by other shell scripts
# (don't put any code here, just variables)
# TODO: consider using python-dotenv

SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export exppath="$SCRIPT_DIR" # path of experiment directory

export study="$(basename "$(realpath "$SCRIPT_DIR")")" # e.g. "default_study"
# base path at which to store any experiments for this user:
export mainpath="/storage/$USER"
# path to this particular experiment:
export studypath="${mainpath}/${study}"


# exps order is the same for all params
#export experiments=("defaultexperiment")
export experiments="defaultexperiment" # comma delimited list
export seasons_conditions=("1.0_1.0_0")
export runs=10
export num_generations="100"
export num_terminals=2 # DO NOT TOUCH

# these params are the same for all exps
# gens for boxplots and snapshots
#export generations=(100)
export generations="100" # comma delimited list
#gen for lineplots
export final_gen=100