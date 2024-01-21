#!/usr/bin/env bash

cat /run/secrets/env_file > .env

uvicorn main:app --host 0.0.0.0 --port 8000