#!/bin/sh
gunicorn --bind 0.0.0.0:5000 wsgi:app &
ngrok http 5000 &
