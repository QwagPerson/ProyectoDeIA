#!/usr/bin/env bash

source config_files/.env.dev
uvicorn main:app --reload --port ${PORT}