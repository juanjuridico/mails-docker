#!/bin/bash
# Script para desplegar en producción

echo "Construyendo imagen Docker..."
docker-compose build

echo "Levantando contenedores..."
docker-compose up -d

echo "Despliegue completado. Usa:"
echo "  docker exec -it mails-docker-app python cli.py generate"
