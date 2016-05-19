#!/bin/bash

set -eux

python askso/server.py &
server_pid=$!
sleep 3

set +e

python test/__init__.py
result=$?
kill $(ps aux | grep askso/server.py | grep -v grep | awk '{print $2}')
exit $result
