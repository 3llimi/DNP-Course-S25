#!/bin/bash

# RabbitMQ Workflow Manager
# Starts all services in order and cleans up on exit
# Shows Producer output in console

# Configuration
LOG_FILE="/dev/null"  # No data stored in files
PYTHON_CMD="python3"
MESSAGE_COUNT=21

# Process IDs storage (in memory only)
declare -A PIDS

# Function to start a service
start_service() {
    local name=$1
    local script=$2
    local args=$3 
    local redirect="$LOG_FILE"
    
    # Special handling for Producer to show output
    if [ "$name" = "Producer" ]; then
        redirect="/dev/stdout"
    fi
    
    echo "Starting $name..."
    if [ -n "$args" ]; then
        $PYTHON_CMD "$script" $args > "$redirect" 2>&1 &
    else
        $PYTHON_CMD "$script" > "$redirect" 2>&1 &
    fi
    PIDS[$name]=$!
}

# Function to clean up processes
cleanup() {
    echo -e "\nShutting down services..."
    for name in "${!PIDS[@]}"; do
        if kill -0 "${PIDS[$name]}" 2>/dev/null; then
            kill -TERM "${PIDS[$name]}" 2>/dev/null && echo "Stopped $name"
        fi
    done
    # Wait for processes to terminate
    sleep 2
    # Force kill any remaining processes
    for name in "${!PIDS[@]}"; do
        if kill -0 "${PIDS[$name]}" 2>/dev/null; then
            kill -KILL "${PIDS[$name]}" 2>/dev/null && echo "Force stopped $name"
        fi
    done
}

# Trap CTRL+C and other termination signals
trap cleanup INT TERM EXIT

run_tests(){
    echo "Producer finished Producing"

    # Log Verification Script
    # Checks that original numbers match their squared and cubed counterparts

    LOG_FILE="rabbitmq_messages.log"
    TEMP_FILE="/tmp/verify_temp.log"
    NAME_FILTER="test1"  # Change this to filter by different names

    # Check if log file exists
    if [ ! -f "$LOG_FILE" ]; then
        echo "Success: Log file $LOG_FILE not found!"
        exit 0
    else
        echo "Error: Log file $LOG_FILE found!"
        exit 1
    fi

    
}

[ -e "rabbitmq_messages.log" ] && rm "rabbitmq_messages.log"
# Start services in proper order
# start_service "Logger" "applications/Logger.py" # Don't start logger
start_service "Squarer" "applications/Squarer.py"
start_service "Cuber" "applications/Cuber.py"
sleep 1  # Give it a moment to initialize
start_service "Producer" "applications/Producer.py" "test1 $MESSAGE_COUNT 0.0"

echo "All services running. Press CTRL+C to stop."
echo "------------------------------------------"

# Keep script running while services work
while true; do
    sleep 1
    # Check if any critical process died
    for name in "${!PIDS[@]}"; do
        if ! kill -0 "${PIDS[$name]}" 2>/dev/null; then
            if [ "$name" = "Producer" ]; then
                run_tests
            else
                echo "ERROR: $name died!"
                cleanup
                exit 1
            fi
        fi
    done
done
