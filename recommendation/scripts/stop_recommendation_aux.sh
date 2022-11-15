#!/bin/bash
PID=$(netstat -tlnp | awk '/:1111 */ {split($NF,a,"/"); print a[1]}')
[ -z "$PID" ] && echo "Recommendation Aux service is not running" || (echo "Stopping Recommendation Aux service at port 9090 and pid $PID" && kill $PID)
