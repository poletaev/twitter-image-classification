#!/bin/bash

celery -A classify_tweets.app worker -l info -Q russir,celery --config=worker_default.py
