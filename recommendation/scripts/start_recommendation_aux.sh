#!/bin/bash
echo "Starting Recommendation Aux service..."
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
LOG=$DIR/../../../log_aux.txt
cd $DIR/../..
nohup python3 -m recommendation.processService.RecommendationAuxServer >> $LOG 2>&1  &
echo Recommendation Aux service started at port 1111 and pid $!
echo  $(date)  service started at port 1111 and pid $! >> $LOG
