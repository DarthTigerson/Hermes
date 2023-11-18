#!/bin/bash

if [ ! -e db/hermes.db ]
then
  mkdir db
  python startup.py --overwrite
fi

uvicorn main:app --host 0.0.0.0 --reload