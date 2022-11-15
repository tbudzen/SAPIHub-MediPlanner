#!/bin/bash
sudo nohup python3 db_server.py >> log.txt 2>&1 &
echo $(date) Anotation service started at port 8090 and pid $!
echo  $(date) Anotation service started at port 8090 and pid $! >> log.txt
