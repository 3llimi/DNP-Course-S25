#!/bin/bash

echo "-------------------"
echo "Test 1: Essentials"
echo "-------------------"

# Check file existence
echo "Checking if server.py exists in the correct location"
if ! test -f server/server.py; then
    echo "File does not exist: server/server.py"
    exit 1
fi

# Installing autopep8
echo "Installing autopep8"
if ! pip install --no-cache-dir autopep8; then
    echo "Failed to install autopep8"
    exit 1
fi

# Checking code formatting
if ! autopep8 --exit-code -i -a server/server.py; then
    echo "Your source code at server/server.py is not formatted according to PEP8"
    echo "Run 'autopep8 -i -a server/server.py' to fix"
    exit 1
fi
