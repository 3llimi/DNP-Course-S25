#!/bin/bash

echo "-------------------"
echo "Test 2: Uploading a note"
echo "-------------------"

# Check file existence
echo "Checking if server.py exists in the correct location"
if ! test -f server/server.py; then
    echo "File does not exist: server/server.py"
    exit 1
fi

echo "Running server in background"
python3 server/server.py 8000 & PID=$!
sleep 2

echo "Uploading note.txt"
python3 client/client.py 127.0.0.1:8000 client/note.txt

echo "Verifying results"
if ! cmp --silent client/note.txt server/note.txt; then
    echo "Files client/note.txt and server/note.txt do not match"
    exit 1
fi

kill -9 $PID
