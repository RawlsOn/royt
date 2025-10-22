#!/bin/sh -ue

# 루트에서
# ./shell/build-local.sh

RUNNING_MODE="local"
PROJECT_NAME="royt"
DOCKER_FILE="docker-compose.$RUNNING_MODE.yml"

# env 파일을 필요한 곳에 모두 복사함
# command="cp ./.env ./docker/; cp ./.env ./api-gateway/; cp ./.env ./front/; cp ./.env ./front/quasar-project/"
command="cp ./.env ./docker/; cp ./.env ./api-gateway/;"
echo $command
eval $command


# build
command="docker-compose -p $PROJECT_NAME -f docker/$DOCKER_FILE --env-file .env build"
# command="docker-compose -p $PROJECT_NAME -f docker/$DOCKER_FILE --env-file .env build --no-cache"
echo $command
eval $command

# docker compose down
command="docker-compose -p $PROJECT_NAME -f docker/$DOCKER_FILE --env-file .env down --remove-orphans"
echo $command
eval $command

# up
command="docker-compose -p $PROJECT_NAME -f docker/$DOCKER_FILE up --remove-orphans"
# command="docker-compose -p $PROJECT_NAME -f docker/$DOCKER_FILE up -d --remove-orphans"
echo $command
eval $command
