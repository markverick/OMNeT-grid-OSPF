#!/bin/bash

# Function to run a command in a new screen
run_in_screen() {
    local N=$1
    screen -dmS "grid-$N" bash -c "python3 run-grid.py $N $N"
}

# Array to keep track of running screens
running_screens=()

# Main loop to run screens
for i in $(seq 1 20); do
    # Run the screen and add its ID to the array
    run_in_screen $i
    running_screens+=($i)

    # If there are 4 screens running, wait for any of them to finish
    while [ ${#running_screens[@]} -ge 4 ]; do
        sleep 1  # Briefly sleep to avoid tight loop

        # Check which screens are still running
        for j in "${!running_screens[@]}"; do
            if ! screen -list | grep -q "grid-${running_screens[j]}"; then
                # Remove finished screen from the array
                unset running_screens[j]
                # Rebuild the array to remove gaps
                running_screens=("${running_screens[@]}")
                break
            fi
        done
    done
done

echo "All screens started."
