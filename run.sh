#!/bin/bash

test -e hermes.db && python startup.py

uvicorn main:app --reload