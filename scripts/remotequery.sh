#!/usr/bin/env bash

echo "running remote query with sql file $1, results are saved in remotequery_result.csv. Remember: Should be run on server with nohup and & at end. Example: nohup ./remotequery.sh SQLFILE.sql &"
psql -h 172.19.1.104 -p 4102 -U smartmi -d ev_smartmi -f $1 -o remotequery_result.csv
