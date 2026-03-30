#!/bin/sh
tailwindcss -i /app/static/css/input.css -o /app/static/css/output.css --watch &
uv run python manage.py runserver 0.0.0.0:8000