#!/bin/bash

# StarBurger deployment script.

set -Eeuo pipefail

check for sudo privileges
if [[ $UID != 0 ]]; then
    echo "Please run this script with sudo:"
    echo "sudo -E $0 $*"
    exit 1
fi

check for avaliable rollbar token
if [ -z "${ROLLBAR_SERVER_POST_TOKEN+x}" ]; then
    echo -e "ROLLBAR_SERVER_POST_TOKEN is not set.\n\nExport the variable and use:\n"
    echo -e "sudo -E $0 $*\n"
    echo -e "or pass it directly:\n"
    echo "sudo ROLLBAR_SERVER_POST_TOKEN=rollbar_token $0 $*"
    exit 1
fi

echo "Start deploying Starburger."

sudo systemctl stop star-burger.service

docker-compose down

# git checkout master
# git pull --rebase

docker-compose up --build -d

docker-compose exec backend python manage.py collectstatic --noinput
docker-compose exec backend python manage.py migrate --noinput

docker-compose stop

sudo systemctl restart star-burger.service
sudo systemctl reload nginx.service

curl -H "X-Rollbar-Access-Token: $ROLLBAR_SERVER_POST_TOKEN"\
     -H "Content-Type: application/json"\
     -X POST 'https://api.rollbar.com/api/1/deploy'\
     -d '{
    "environment": "production",
    "revision": "'"$(git rev-parse --short --verify HEAD)"'",
    "rollbar_name": "lypavel",
    "local_username": "lypavel",
    "comment": "automated deployment via shell script",
    "status": "succeeded"
}'

echo  # new line
echo "Successfully deployed StarBurger"