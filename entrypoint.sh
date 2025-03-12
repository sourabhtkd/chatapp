#! /bin/bash

# Run database migrations
python3 manage.py makemigratios ; python3 manage.py migrate

# Start the application
#exec daphne -b 0.0.0.0 -p 8000 core.asgi:application
python3 manage.py runserver 0.0.0.0:8000