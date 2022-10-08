#!/bin/bash
set -e
#set -x

SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/vars.sh" # read variables
#runs=10

# discover unfinished experiments

to_do=()
for i in $(seq $runs)
do
    run=$(($i))

    for experiment in "${experiments[@]}"
    do

     printf  "\n${experiment}_${run} \n"
     file="/storage/${mainpath}/${study}/${experiment}_${run}.log";

     #check experiments status
     if [[ -f "$file" ]]; then
        lastgen=$(grep -c "Finished generation" $file);
        echo " latest finished gen ${lastgen}";
     else
         # not started yet
         echo " None";
     fi

    done
done
