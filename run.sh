#!/bin/bash

# If database is not set, start it
if [ ! -e db/hermes.db ]
then
  mkdir db
  python startup.py --overwrite
fi

# If no params were given, run on dev mode
if [ $# -eq 0 ]
then
  uvicorn main:app --host 0.0.0.0 --reload
fi

# If two params were given, run in production secure mode
if [ $# -eq 2 ]
then
  uvicorn main:app --host 0.0.0.0 --port 443 --ssl-keyfile="$1"  --ssl-certfile="$2"
fi