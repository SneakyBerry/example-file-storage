#!/bin/sh
docker-compose rm -fs postgres
set -e
docker-compose up -d postgres
export COMMIT_HASH=$(git rev-parse HEAD)
docker build . -t $COMMIT_HASH
docker run --network=file_storage_file_storage --env-file=./.env $COMMIT_HASH /src/scripts/migrate.sh
docker run --network=file_storage_file_storage --env-file=./.env $COMMIT_HASH /src/scripts/test.sh
docker-compose up