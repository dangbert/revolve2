#!/bin/bash

set -e
# delimiter is comma, example:
#experiments="exp1,epx2"
# exps order is the same for all params
SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/vars.sh" # read variables

#export experiments=("defaultexperiment")
#export experiments="exp1,epx2"
python3 "${exppath}/snapshots_bests.py" # $study $experiments $runs $generations $mainpath;
python3 "${exppath}/bests_snap_2d.py" # $study $experiments $runs $generations $mainpath;
python3 "${exppath}/consolidate.py" # $study $experiments $runs $final_gen $mainpath;
python3 "${exppath}/plot_static.py" # $study $experiments $runs $generations $mainpath;
#