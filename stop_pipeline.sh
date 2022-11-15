#!/bin/bash
PID=$(sudo netstat -tlnp | awk '/:8090 */ {split($NF,a,"/"); print a[1]}')
[ -z "$PID" ] && echo "Anotation service is not running" || (echo "Stopping anotation service at port 8090 and pid $PID" && sudo kill $PID)
