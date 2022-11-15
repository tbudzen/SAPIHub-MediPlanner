#!/bin/bash
git reset --hard
git pull
./stop_pipeline.sh
./start_pipeline.sh

