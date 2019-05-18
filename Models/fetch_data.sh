#!/usr/bin/env bash
export PGPASSWORD='63p467R=530'
psql -h 172.19.1.104 -p 4102 -U smartmi -d ev_smartmi -f ../SQL/fetch_data_updated.sql
python SplitTrainTest.py
