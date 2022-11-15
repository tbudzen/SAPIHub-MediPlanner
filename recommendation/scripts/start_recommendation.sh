#!/bin/bash
echo "Starting Recommendation service..."
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
LOG=$DIR/../../../log.txt
cd $DIR/../..
nohup python3 -m recommendation.processService.RecommendationServer >> $LOG 2>&1  &
echo Recommendation service started at port 9090 and pid $!
echo  $(date)  service started at port 9090 and pid $! >> $LOG
