#!/bin/bash

if [ ! -d db ]
then
  mkdir db
  python startup.py --overwrite
fi

uvicorn main:app --reload