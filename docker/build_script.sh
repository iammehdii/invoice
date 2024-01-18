#!/bin/bash

# Accessing the SERVICES variable and splitting it into an array
#CI_SERVICES="django,postgresql,nginx"
#CI_CONTAINER_REGISTRY="$1"
#CI_PROJECT_ROOT="$2"
#CI_PROJECT_NAME="$3"
#CI_STACK_NAME="$4"
#CI_SERVICES="$5"

echo Services: "${CI_SERVICES}"
IFS=, read -ra SERVICE_ARRAY <<<"$CI_SERVICES"

for SERVICE_NAME in "${SERVICE_ARRAY[@]}"; do
  echo "Push ${SERVICE_NAME} image to repository."
  docker push "${CI_CONTAINER_REGISTRY}/${SERVICE_NAME}:latest"
done
