#!/bin/bash

echo "-------------------"
echo "Test 3: Uploading an image"
echo "-------------------"

# Check file existence
echo "Checking if server.py exists in the correct location"
if ! test -f server/server.py; then
    echo "File does not exist: server/server.py"
    exit 1
fi

echo "Running server in background"
python3 server/server.py 8001 & PID=$!
sleep 2

echo "Uploading image.png"
python3 client/client.py 127.0.0.1:8001 client/image.png

echo "Verifying results"
if ! cmp --silent client/image.png server/image.png; then
    echo "Files client/image.png and server/image.png do not match"
    exit 1
fi

kill -9 $PID