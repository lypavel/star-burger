#!/bin/bash

docker-compose down

docker-compose up --build -d

echo 'Waiting for database'
sleep 5

until docker-compose exec backend python manage.py migrate --noinput; do
    echo 'Looks like database is not initialized yet. Retrying...'
    sleep 5
done

echo 'Restarting containers to fix network issues'
sleep 5

docker-compose restart

echo 'Done!'