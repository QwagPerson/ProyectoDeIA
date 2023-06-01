#!/usr/bin/env bash

source config_files/.env.dev
export ENVIRONMENT=dev
uvicorn main:app --reload --port ${PORT}
```