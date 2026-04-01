#!/bin/bash

echo "-------------------"
echo "Test 4: Packet loss"
echo "-------------------"

# Check file existence
echo "Checking if server.py exists in the correct location"
if ! test -f server/server.py; then
    echo "File does not exist: server/server.py"
    exit 1
fi

echo "Introducing delay and packet loss"
tc qdisc add dev lo root netem loss 15% delay 500ms

echo "Running server in background"
python3 server/server.py 8002 & PID=$!

echo "Uploading image.png"
python3 client/client.py 127.0.0.1:8002 client/image.png

echo "Checking results"
if ! cmp --silent client/image.png server/image.png; then
    echo "Files client/image.png and server/image.png do not match"
    exit 1
fi

tc qdisc del dev lo root netem loss 15% delay 500ms
kill -9 $PID
