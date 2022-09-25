#!/bin/bash
#set -e
#set -x

SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/vars.sh" # read variables

# DO NOT use underline ( _ ) in the experiments names
# delimiter is space, example:
#experiments=("exp1" "epx2")
# exps order is the same for all params

function main () {
    experiments=("defaultexperiment")
    seasons_conditions=("1.0_1.0_0")
    runs=10
    num_generations="100"

    num_terminals=2

    mkdir "${studypath}/analysis"

    possible_screens=()

    # defines possible ports for screens
    for t in $(seq 1 $((${num_terminals}))); do
        possible_screens+=($t)
    done


    while true; do
        printf "\n  >>>> loop ... \n"

        # discover free terminals
        active_screens=()
        free_screens=()
        active_experiments=()
        declare -a arr="$(screen -list)"

        for obj in ${arr[@]}; do
            if [[ "$obj" == *"screen_"* ]]; then
            printf "\n screen ${obj} is on\n"
            screen="$(cut -d'_' -f2 <<<"$obj")"
            active_experiments+=("$(cut -d'_' -f3 -<<<"$obj")_$(cut -d'_' -f4 -<<<"$obj")")
            active_screens+=($screen)
            fi
        done

        for possible_screen in "${possible_screens[@]}"; do
            if [[ ! " ${active_screens[@]} " =~ " ${possible_screen} " ]]; then
                free_screens+=($possible_screen)
            fi
        done

        # discover unfinished experiments
        to_do=()
        unfinished=()
        for i in $(seq $runs); do
            run=$(($i))

            for experiment in "${experiments[@]}"; do
                printf  "\n${experiment}_${run} \n"
                file="${mainpath}/${study}/${experiment}_${run}.log";

                #check experiments status
                if [[ -f "$file" ]]; then

                    lastgen=$(grep -c "Finished generation" $file);
                    echo "latest finished gen ${lastgen}";

                    if [ "$lastgen" -lt "$num_generations" ]; then
                        unfinished+=("${experiment}_${run}")

                        # only if not already running
                        if [[ ! " ${active_experiments[@]} " =~ " ${experiment}_${run} " ]]; then
                        to_do+=("${experiment}_${run}")
                        fi
                    fi
                else
                    # not started yet
                    echo " None";
                    unfinished+=("${experiment}_${run}")
                    # only if not already running
                        if [[ ! " ${active_experiments[@]} " =~ " ${experiment}_${run} " ]]; then
                        to_do+=("${experiment}_${run}")
                        fi
                fi
            done
        done


        # spawns N experiments (N is according to free screens)
        max_fs=${#free_screens[@]}
        to_do_now=("${to_do[@]:0:$max_fs}")
        p=0
        for to_d in "${to_do_now[@]}"; do
            exp=$(cut -d'_' -f1 <<<"${to_d}")
            run=$(cut -d'_' -f2 <<<"${to_d}")
            idx=$( echo ${experiments[@]/${exp}//} | cut -d/ -f1 | wc -w | tr -d ' ' )

            # nice -n19 python3  experiments/${study}/optimize.py
            printf "\n >> (re)starting screen_${free_screens[$p]}_${to_d} \n\n"
            screen -d -m -S screen_${free_screens[$p]}_${to_d} -L -Logfile "${studypath}/${exp}_${run}.log" python3 "$exppath/optimize.py" \
                --experiment_name "${exp}" --seasons_conditions "${seasons_conditions[$idx]}" --run "${run}" "--study=${study}" --num_generations "${num_generations}";

            p=$((${p}+1))
        done

        # if all experiments are finished, makes video
        if [ -z "$unfinished" ]; then
            file="${studypath}/analysis/video_bests.mpg";

            if [ -f "$file" ]; then
                printf ""
            else
                printf " \n making video..."
                screen -d -m -S videos ffmpeg -f x11grab -r 25 -i :1 -qscale 0 $file;
                python3 experiments/${study}/watch_robots.py;
                killall screen;
                printf " \n finished video!"
            fi
        fi
        sleep 1800;
    done

    # run from revolve root
    # screen -ls  | egrep "^\s*[0-9]+.screen_" | awk -F "." '{print $1}' |  xargs kill
    # killall screen
    # screen -r naaameee
    # screen -list
}

main "$@"
