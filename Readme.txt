cd /docker/Dockerfile
docker compose docker-compose.yml build
docker compose docker-compose.yml up -d
curl --request POST --data-binary "@pdf-filename.pdf" http://localhost:8003/invoice?kind=invoice
