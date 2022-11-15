#!/bin/bash
PID=$(netstat -tlnp | awk '/:9090 */ {split($NF,a,"/"); print a[1]}')
[ -z "$PID" ] && echo "Recommendation service is not running" || (echo "Stopping Recommendation service at port 9090 and pid $PID" && kill $PID)
