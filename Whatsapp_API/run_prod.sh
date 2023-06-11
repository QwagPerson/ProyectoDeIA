#!/usr/bin/env bash

export ENVIRONMENT=prod
gunicorn main:app -c ./config_files/gunicorn.conf.py